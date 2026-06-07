$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $PSScriptRoot
$projectTessdata = Join-Path $root "backend\ocr_data\tessdata"

Write-Host "Checking OCR runtime..." -ForegroundColor Cyan

function Test-Command($Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "[OK] $Name found: $($cmd.Source)" -ForegroundColor Green
        return $true
    }
    Write-Host "[MISSING] $Name not found on PATH" -ForegroundColor Yellow
    return $false
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

    $candidates = @()
    if ($env:LOCALAPPDATA) {
        $wingetRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
        if (Test-Path $wingetRoot) {
            $candidates += Get-ChildItem $wingetRoot -Directory -Filter "poppler-*" -ErrorAction SilentlyContinue |
                ForEach-Object { Join-Path $_.FullName "Library\bin" }
        }
    }
    $candidates += @(
        "C:\Program Files\poppler\Library\bin",
        "C:\Program Files\poppler\bin",
        "C:\Program Files (x86)\poppler\Library\bin",
        "C:\Program Files (x86)\poppler\bin"
    )
    foreach ($candidate in $candidates) {
        if ((Test-Path (Join-Path $candidate "pdfinfo.exe")) -and (Test-Path (Join-Path $candidate "pdftoppm.exe"))) {
            return $candidate
        }
    }
    return $null
}

$tesseractPath = Find-Tesseract
$popplerBin = Find-PopplerBin

if ($tesseractPath) {
    Write-Host "[OK] tesseract found: $tesseractPath" -ForegroundColor Green
    $tesseractOk = $true
} else {
    Write-Host "[MISSING] tesseract not found" -ForegroundColor Yellow
    $tesseractOk = $false
}

if ($popplerBin) {
    Write-Host "[OK] Poppler found: $popplerBin" -ForegroundColor Green
    $pdfinfoOk = $true
    $pdftoppmOk = $true
} else {
    Write-Host "[MISSING] Poppler pdfinfo/pdftoppm not found" -ForegroundColor Yellow
    $pdfinfoOk = $false
    $pdftoppmOk = $false
}

$chiSimOk = Test-Path (Join-Path $projectTessdata "chi_sim.traineddata")
$engOk = Test-Path (Join-Path $projectTessdata "eng.traineddata")
if ($chiSimOk -and $engOk) {
    Write-Host "[OK] Project OCR languages found: chi_sim + eng" -ForegroundColor Green
} else {
    Write-Host "[MISSING] Project OCR languages need setup: $projectTessdata" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking Python OCR packages..." -ForegroundColor Cyan
$backendPython = Join-Path $root "backend\.venv\Scripts\python.exe"
$pythonCmd = if (Test-Path $backendPython) { $backendPython } else { "python" }
& $pythonCmd -c "import importlib.util; names=['rapidocr_onnxruntime','onnxruntime','pytesseract','PIL','pdf2image','pypdf','docx','pptx']; [print(f'[OK] {n}' if importlib.util.find_spec(n) else f'[MISSING] {n}') for n in names]"

Write-Host ""
if ($tesseractOk -and $pdfinfoOk -and $pdftoppmOk -and $chiSimOk -and $engOk) {
    Write-Host "OCR runtime looks ready." -ForegroundColor Green
} else {
    Write-Host "Install missing tools if you need image OCR or scanned PDF OCR:" -ForegroundColor Yellow
    Write-Host "  .\scripts\install-ocr.ps1"
}
