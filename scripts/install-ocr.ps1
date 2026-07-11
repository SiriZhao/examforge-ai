$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$projectTessdata = Join-Path $root "backend\ocr_data\tessdata"
$chiSimUrl = "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata"

function Write-Step($message) {
    Write-Host ""
    Write-Host "==> $message" -ForegroundColor Cyan
}

function Find-Tesseract {
    $cmd = Get-Command "tesseract" -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }

    $candidates = @(
        "C:\Program Files\Tesseract-OCR\tesseract.exe",
        "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

function Find-PopplerBin {
    $cmd = Get-Command "pdfinfo" -ErrorAction SilentlyContinue
    if ($cmd) { return Split-Path -Parent $cmd.Source }

    if ($env:LOCALAPPDATA) {
        $wingetRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
        if (Test-Path $wingetRoot) {
            $match = Get-ChildItem $wingetRoot -Directory -Filter "poppler-*" -ErrorAction SilentlyContinue |
                ForEach-Object { Join-Path $_.FullName "Library\bin" } |
                Where-Object { Test-Path (Join-Path $_ "pdfinfo.exe") } |
                Select-Object -First 1
            if ($match) { return $match }
        }
    }
    return $null
}

function Install-WithWinget($id) {
    if (-not (Get-Command "winget" -ErrorAction SilentlyContinue)) {
        throw "winget is required for automatic OCR runtime installation."
    }
    winget install --id $id --source winget --accept-package-agreements --accept-source-agreements
}

Write-Host "ExamForge AI OCR installer" -ForegroundColor Green

if (-not (Find-Tesseract)) {
    Write-Step "Installing Tesseract OCR"
    Install-WithWinget "tesseract-ocr.tesseract"
} else {
    Write-Step "Tesseract OCR already installed"
}

if (-not (Find-PopplerBin)) {
    Write-Step "Installing Poppler for scanned PDF OCR"
    Install-WithWinget "oschwartz10612.Poppler"
} else {
    Write-Step "Poppler already installed"
}

Write-Step "Preparing project OCR language data"
New-Item -ItemType Directory -Force -Path $projectTessdata | Out-Null

$tesseractPath = Find-Tesseract
$systemTessdata = if ($tesseractPath) { Join-Path (Split-Path -Parent $tesseractPath) "tessdata" } else { "" }

foreach ($lang in @("eng", "osd")) {
    $source = Join-Path $systemTessdata "$lang.traineddata"
    $target = Join-Path $projectTessdata "$lang.traineddata"
    if ((Test-Path $source) -and (-not (Test-Path $target))) {
        Copy-Item -LiteralPath $source -Destination $target -Force
    }
}

$chiSimTarget = Join-Path $projectTessdata "chi_sim.traineddata"
if (-not (Test-Path $chiSimTarget)) {
    Write-Step "Downloading Simplified Chinese OCR language data"
    curl.exe --ssl-no-revoke -L $chiSimUrl -o $chiSimTarget
}

Write-Step "Final OCR check"
& (Join-Path $PSScriptRoot "check-ocr.ps1")
