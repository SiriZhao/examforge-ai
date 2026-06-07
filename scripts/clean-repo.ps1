param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$deleted = New-Object System.Collections.Generic.List[string]

function Convert-ToRelativePath {
    param([string]$Path)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $rootPath = [System.IO.Path]::GetFullPath($root)
    if (-not $rootPath.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $rootPath += [System.IO.Path]::DirectorySeparatorChar
    }
    $rootUri = New-Object System.Uri($rootPath)
    $pathUri = New-Object System.Uri($fullPath)
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString()) -replace '\\', '/'
}

function Remove-RepoItem {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $resolved = (Resolve-Path -LiteralPath $Path).Path
    $rootResolved = (Resolve-Path -LiteralPath $root).Path
    if (-not ($resolved -eq $rootResolved -or $resolved.StartsWith($rootResolved + [System.IO.Path]::DirectorySeparatorChar))) {
        throw "Refusing to remove path outside project root: $resolved"
    }

    $deleted.Add((Convert-ToRelativePath $resolved)) | Out-Null
    if (-not $DryRun) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}

function Clear-DirectoryExceptGitkeep {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
        }
    }

    if (Test-Path -LiteralPath $Path) {
        Get-ChildItem -LiteralPath $Path -Force |
            Where-Object { $_.Name -ne ".gitkeep" } |
            ForEach-Object { Remove-RepoItem $_.FullName }
    }

    $gitkeep = Join-Path $Path ".gitkeep"
    if (-not (Test-Path -LiteralPath $gitkeep) -and -not $DryRun) {
        New-Item -ItemType File -Path $gitkeep -Force | Out-Null
    }
}

$pathsToRemove = @(
    "backend/.venv",
    "frontend/node_modules",
    "frontend/dist",
    "build",
    "dist",
    "backend/.pytest_cache",
    "backend/dev-server.log",
    "backend/dev-server.err.log",
    "frontend/dev-server.log",
    "frontend/dev-server.err.log",
    "frontend/tsconfig.tsbuildinfo"
)

foreach ($relativePath in $pathsToRemove) {
    Remove-RepoItem (Join-Path $root $relativePath)
}

Get-ChildItem -LiteralPath (Join-Path $root "backend") -Directory -Filter "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue |
    ForEach-Object { Remove-RepoItem $_.FullName }

Clear-DirectoryExceptGitkeep (Join-Path $root "backend/uploads")
Clear-DirectoryExceptGitkeep (Join-Path $root "backend/outputs")
Clear-DirectoryExceptGitkeep (Join-Path $root "backend/ocr_data/tessdata")

if ($deleted.Count -eq 0) {
    Write-Host "Repository is already clean."
} else {
    Write-Host "Removed items:"
    $deleted | Sort-Object | ForEach-Object { Write-Host "  $_" }
}

if ($DryRun) {
    Write-Host ""
    Write-Host "Dry run only; no files were removed."
}
