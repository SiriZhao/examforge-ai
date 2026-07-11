$ErrorActionPreference = "Continue"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
. (Join-Path $PSScriptRoot "local-tools.ps1")

Write-Host "正在停止 CampusForge 本地服务..." -ForegroundColor Cyan
Stop-PortOwner 8000
Stop-PortOwner 5173
Start-Sleep -Seconds 2
Write-Host "本地服务清理完成。" -ForegroundColor Green
