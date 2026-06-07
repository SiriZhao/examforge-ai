param([switch]$NoPause)

$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
. (Join-Path $PSScriptRoot "local-tools.ps1")

function Clear-KeepGitkeep {
    param([string]$Path)
    if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
    Get-ChildItem -LiteralPath $Path -Force | Where-Object { $_.Name -ne ".gitkeep" } | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }
    $gitkeep = Join-Path $Path ".gitkeep"
    if (-not (Test-Path $gitkeep)) { New-Item -ItemType File -Path $gitkeep -Force | Out-Null }
}

Write-Host "正在清理本地运行数据..." -ForegroundColor Cyan
Clear-KeepGitkeep (Join-Path $ProjectRoot "backend\uploads")
Clear-KeepGitkeep (Join-Path $ProjectRoot "backend\outputs")

$cacheDirs = @((Join-Path $ProjectRoot "backend\.pytest_cache"), (Join-Path $ProjectRoot "frontend\dist"))
foreach ($cacheDir in $cacheDirs) {
    if (Test-Path $cacheDir) { Remove-Item -LiteralPath $cacheDir -Recurse -Force; Write-Ok "已清理：$cacheDir" }
}

Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "backend") -Directory -Filter "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -LiteralPath $_.FullName -Recurse -Force
    Write-Ok "已清理：$($_.FullName)"
}

Write-Ok "uploads 已清空并保留 .gitkeep"
Write-Ok "outputs 已清空并保留 .gitkeep"
Write-Host "本地数据重置完成。" -ForegroundColor Green
Pause-IfNeeded -NoPause:$NoPause