param(
    [switch]$SkipTests,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$backendVenv = Join-Path $backend ".venv"
$pythonExe = Join-Path $backendVenv "Scripts\python.exe"
$distDir = Join-Path $root "dist"
$buildDir = Join-Path $root "build"
$installerOut = Join-Path $distDir "installer"
$appVersion = "0.4.0"

function Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Assert-Command {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. $Hint"
    }
}

function Find-InnoCompiler {
    $cmd = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) { return $candidate }
    }
    return $null
}

function Stop-RunningExamForge {
    $running = Get-Process -Name "ExamForgeAI" -ErrorAction SilentlyContinue
    if (-not $running) { return }

    Write-Host "ExamForgeAI.exe is running. Attempting to stop it before rebuilding..." -ForegroundColor Yellow
    foreach ($process in $running) {
        try {
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
        } catch {
            throw "ExamForgeAI.exe is currently running and could not be stopped. Please close ExamForge AI and rerun scripts\build-windows.ps1."
        }
    }
    Start-Sleep -Seconds 1
}

Push-Location $root
try {
    Step "Clean old build artifacts"
    Stop-RunningExamForge
    if (Test-Path $distDir) { Remove-Item -LiteralPath $distDir -Recurse -Force }
    if (Test-Path $buildDir) { Remove-Item -LiteralPath $buildDir -Recurse -Force }
    New-Item -ItemType Directory -Path $installerOut -Force | Out-Null

    Assert-Command "python" "Install Python 3.11+."
    Assert-Command "npm" "Install Node.js LTS."

    Step "Install frontend dependencies"
    Push-Location $frontend
    npm install
    Pop-Location

    Step "Build frontend static files"
    Push-Location $frontend
    npm run build
    Pop-Location

    Step "Prepare backend virtual environment"
    if (-not (Test-Path $pythonExe)) {
        Push-Location $backend
        python -m venv .venv
        Pop-Location
    }

    Step "Install backend dependencies and packaging tools"
    Push-Location $backend
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r requirements.txt
    & $pythonExe -m pip install pyinstaller
    Pop-Location

    if (-not $SkipTests) {
        Step "Run backend tests"
        Push-Location $backend
        & $pythonExe -m pytest
        Pop-Location

        Step "Run frontend tests"
        Push-Location $frontend
        npm run test -- --run
        Pop-Location
    }

    Step "Build Windows executable with PyInstaller"
    & $pythonExe -m PyInstaller ExamForgeAI.spec --noconfirm

    $exePath = Join-Path $distDir "ExamForgeAI.exe"
    if (-not (Test-Path $exePath)) {
        throw "PyInstaller did not produce $exePath"
    }
    Write-Host "Executable: $exePath" -ForegroundColor Green

    if (-not $SkipInstaller) {
        $iscc = Find-InnoCompiler
        if ($iscc) {
            Step "Build installer with Inno Setup"
            & $iscc (Join-Path $root "installer\exam-review-agent.iss")
            if ($LASTEXITCODE -ne 0) {
                throw "Inno Setup failed with exit code $LASTEXITCODE."
            }
            $setupPath = Join-Path $installerOut "ExamForgeAISetup-$appVersion.exe"
            if (Test-Path $setupPath) {
                Write-Host "Installer: $setupPath" -ForegroundColor Green
            } else {
                throw "Inno Setup completed, but installer output was not found at $setupPath"
            }
        } else {
            Write-Host "Inno Setup compiler was not found. Skipping installer build." -ForegroundColor Yellow
            Write-Host "Install Inno Setup 6 and rerun this script to create dist\installer\ExamForgeAISetup-$appVersion.exe."
        }
    }

    Write-Host ""
    Write-Host "Windows packaging completed." -ForegroundColor Green
    Write-Host "EXE: dist\ExamForgeAI.exe"
    Write-Host "Installer: dist\installer\ExamForgeAISetup-$appVersion.exe"
} finally {
    Pop-Location
}

