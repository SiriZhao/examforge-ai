$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Command
}

Invoke-Step "Backend tests" {
    Push-Location $backend
    try {
        python -m pytest
    } finally {
        Pop-Location
    }
}

Invoke-Step "Frontend tests" {
    Push-Location $frontend
    try {
        npm run test -- --run
    } finally {
        Pop-Location
    }
}

Invoke-Step "Frontend build" {
    Push-Location $frontend
    try {
        npm run build
    } finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "All tests and builds passed." -ForegroundColor Green
