param(
    [switch]$NoPause
)

$ErrorActionPreference = "Continue"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
. (Join-Path $PSScriptRoot "local-tools.ps1")

function Print-Result {
    param($Result)
    if ($Result.Ok) { Write-Ok $Result.Message } else { Write-Fail $Result.Message }
}

Write-Host "CampusForge 诊断报告" -ForegroundColor Green
Write-Host "项目目录：$ProjectRoot"
Write-Host "诊断时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

Write-Title "基础环境"
Print-Result (Test-Python)
Print-Result (Test-Node)
Print-Result (Test-CommandAvailable "pip" "未找到 pip。请重新安装 Python，并确认 pip 已启用。")
Print-Result (Test-CommandAvailable "npm" "未找到 npm。请安装 Node.js LTS。")

Write-Title "项目依赖"
Print-Result (Test-BackendDependencies)
Print-Result (Test-FrontendDependencies)

Write-Title "OCR 环境"
foreach ($result in Test-OcrEnvironment) {
    if ($result.Ok) { Write-Ok $result.Message } else { Write-Warn $result.Message }
}

Write-Title "端口状态"
Print-Result (Test-PortFree 8000)
Print-Result (Test-PortFree 5173)

Write-Title "目录状态"
$paths = @(
    @{ Name = "后端上传目录"; Path = Join-Path $ProjectRoot "backend\uploads" },
    @{ Name = "后端输出目录"; Path = Join-Path $ProjectRoot "backend\outputs" },
    @{ Name = "OCR 数据目录"; Path = Join-Path $ProjectRoot "backend\ocr_data\tessdata" },
    @{ Name = "前端 node_modules"; Path = Join-Path $ProjectRoot "frontend\node_modules" },
    @{ Name = "后端虚拟环境"; Path = Join-Path $ProjectRoot "backend\.venv" }
)
foreach ($item in $paths) {
    if (Test-Path $item.Path) { Write-Ok "$($item.Name) 存在：$($item.Path)" } else { Write-Warn "$($item.Name) 不存在：$($item.Path)" }
}

Write-Host ""
Write-Host "诊断完成。若存在 FAIL，请按提示安装缺失环境，或重新双击 start.bat 自动安装依赖。" -ForegroundColor Cyan
Pause-IfNeeded -NoPause:$NoPause
