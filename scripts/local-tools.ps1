$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:BackendDir = Join-Path $script:ProjectRoot "backend"
$script:FrontendDir = Join-Path $script:ProjectRoot "frontend"
$script:BackendVenv = Join-Path $script:BackendDir ".venv"
$script:BackendPython = Join-Path $script:BackendVenv "Scripts\python.exe"

function Write-Title { param([string]$Message) Write-Host ""; Write-Host "== $Message ==" -ForegroundColor Cyan }
function Write-Ok { param([string]$Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Warn { param([string]$Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Fail { param([string]$Message) Write-Host "[FAIL] $Message" -ForegroundColor Red }
function Pause-IfNeeded { param([switch]$NoPause) if (-not $NoPause) { Write-Host ""; Read-Host "Press Enter to close" } }

function Get-CommandPath {
    param([string]$Name)
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    return $null
}

function Get-PythonVersion {
    param([string]$PythonCommand = "python")
    try {
        $output = & $PythonCommand -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
        return [version]($output.Trim())
    } catch { return $null }
}

function Test-Python {
    $path = Get-CommandPath "python"
    if (-not $path) { return [pscustomobject]@{ Ok = $false; Message = "Python was not found. Install Python 3.11+ and enable Add Python to PATH."; Path = $null; Version = $null } }
    $version = Get-PythonVersion "python"
    $ok = $version -and $version -ge [version]"3.11.0"
    return [pscustomobject]@{ Ok = [bool]$ok; Message = if ($ok) { "Python $version" } else { "Python version is too old: $version. Install Python 3.11+." }; Path = $path; Version = $version }
}

function Get-NodeVersion {
    try { return [version]((& node --version 2>$null).TrimStart("v")) } catch { return $null }
}

function Test-Node {
    $path = Get-CommandPath "node"
    if (-not $path) { return [pscustomobject]@{ Ok = $false; Message = "Node.js was not found. Install Node.js LTS."; Path = $null; Version = $null } }
    $version = Get-NodeVersion
    $ok = $version -and $version -ge [version]"18.0.0"
    return [pscustomobject]@{ Ok = [bool]$ok; Message = if ($ok) { "Node.js $version" } else { "Node.js version is too old: $version. Install Node.js 18+." }; Path = $path; Version = $version }
}

function Test-CommandAvailable {
    param([string]$Name, [string]$MissingMessage)
    $path = Get-CommandPath $Name
    return [pscustomobject]@{ Ok = [bool]$path; Message = if ($path) { "$Name found: $path" } else { $MissingMessage }; Path = $path }
}

function Get-PortOwners {
    param([int]$Port)
    try { return @(Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -and $_ -ne 0 }) } catch { return @() }
}

function Test-PortFree {
    param([int]$Port)
    $owners = Get-PortOwners $Port
    return [pscustomobject]@{ Ok = ($owners.Count -eq 0); Port = $Port; Owners = $owners; Message = if ($owners.Count -eq 0) { "Port $Port is available" } else { "Port $Port is occupied by PID(s): $($owners -join ', ')" } }
}

function Stop-ProcessTree {
    param([int]$ProcessId)
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcessId" -ErrorAction SilentlyContinue
    foreach ($child in $children) { Stop-ProcessTree -ProcessId $child.ProcessId }
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
}

function Stop-PortOwner {
    param([int]$Port)
    foreach ($owner in Get-PortOwners $Port) { Write-Warn "Stopping process on port $Port, PID $owner"; Stop-ProcessTree -ProcessId $owner }
}

function Ensure-BackendVenv {
    if (-not (Test-Path $script:BackendPython)) {
        Write-Title "Create backend virtual environment"
        Push-Location $script:BackendDir
        try { python -m venv .venv } finally { Pop-Location }
    }
}

function Install-BackendDependencies {
    Write-Title "Install backend dependencies"
    Push-Location $script:BackendDir
    try { & $script:BackendPython -m pip install --upgrade pip; & $script:BackendPython -m pip install -r requirements.txt } finally { Pop-Location }
}

function Install-FrontendDependencies {
    Write-Title "Install frontend dependencies"
    Push-Location $script:FrontendDir
    try { npm install } finally { Pop-Location }
}

function Test-BackendDependencies {
    if (-not (Test-Path $script:BackendPython)) { return [pscustomobject]@{ Ok = $false; Message = "Backend virtual environment is missing." } }
    try { & $script:BackendPython -c "import fastapi, uvicorn, pydantic, PIL, pypdf, docx, pptx" 2>$null; return [pscustomobject]@{ Ok = $true; Message = "Backend core dependencies can be imported." } } catch { return [pscustomobject]@{ Ok = $false; Message = "Backend dependencies are incomplete. Run start.bat." } }
}

function Test-FrontendDependencies {
    $nodeModules = Join-Path $script:FrontendDir "node_modules"
    $viteBin = Join-Path $nodeModules ".bin\vite.cmd"
    if ((Test-Path $nodeModules) -and (Test-Path $viteBin)) { return [pscustomobject]@{ Ok = $true; Message = "Frontend dependencies are installed." } }
    return [pscustomobject]@{ Ok = $false; Message = "Frontend dependencies are incomplete. Run start.bat." }
}

function Test-OcrEnvironment {
    $results = New-Object System.Collections.Generic.List[object]
    $tesseract = Get-CommandPath "tesseract"
    $pdfinfo = Get-CommandPath "pdfinfo"
    $pdftoppm = Get-CommandPath "pdftoppm"
    $tessdata = Join-Path $script:ProjectRoot "backend\ocr_data\tessdata"
    $chi = Join-Path $tessdata "chi_sim.traineddata"
    $eng = Join-Path $tessdata "eng.traineddata"
    $results.Add([pscustomobject]@{ Ok = [bool]$tesseract; Message = if ($tesseract) { "Tesseract found: $tesseract" } else { "Tesseract was not found. Local Tesseract OCR is unavailable." } }) | Out-Null
    $results.Add([pscustomobject]@{ Ok = [bool]($pdfinfo -and $pdftoppm); Message = if ($pdfinfo -and $pdftoppm) { "Poppler is available." } else { "Poppler was not found. Scanned PDF OCR may be unavailable." } }) | Out-Null
    $results.Add([pscustomobject]@{ Ok = [bool]((Test-Path $chi) -and (Test-Path $eng)); Message = if ((Test-Path $chi) -and (Test-Path $eng)) { "OCR language data chi_sim + eng exists." } else { "OCR language data is missing. Run scripts\install-ocr.ps1 if needed." } }) | Out-Null
    return $results
}