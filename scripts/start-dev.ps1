param(
    [switch]$NoPause,
    [switch]$NoBrowser,
    [switch]$SkipOcrInstall
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
. (Join-Path $PSScriptRoot "local-tools.ps1")

function Assert-Check {
    param($Result)
    if ($Result.Ok) { Write-Ok $Result.Message } else { Write-Fail $Result.Message; throw $Result.Message }
}

function Wait-ForUrl {
    param([string]$Url, [string]$Name, [int]$Seconds = 40)
    for ($i = 0; $i -lt $Seconds; $i++) {
        try { Invoke-RestMethod -Uri $Url -TimeoutSec 2 | Out-Null; Write-Ok "$Name 已启动：$Url"; return $true } catch { Start-Sleep -Seconds 1 }
    }
    return $false
}

try {
    Write-Host "CampusForge 本地启动器" -ForegroundColor Green
    Write-Host "项目目录：$ProjectRoot"

    Write-Title "检查运行环境"
    Assert-Check (Test-Python)
    Assert-Check (Test-Node)
    Assert-Check (Test-CommandAvailable "pip" "未找到 pip。请重新安装 Python，并勾选 pip 与 Add Python to PATH。")
    Assert-Check (Test-CommandAvailable "npm" "未找到 npm。请安装 Node.js LTS。")

    Write-Title "检查端口占用"
    $backendPort = Test-PortFree 8000
    $frontendPort = Test-PortFree 5173
    if (-not $backendPort.Ok -or -not $frontendPort.Ok) {
        Write-Warn "检测到端口被占用，将尝试停止旧的本地服务。"
        Stop-PortOwner 8000
        Stop-PortOwner 5173
        Start-Sleep -Seconds 2
    }
    Assert-Check (Test-PortFree 8000)
    Assert-Check (Test-PortFree 5173)

    Ensure-BackendVenv
    Install-BackendDependencies
    Install-FrontendDependencies

    if (-not $SkipOcrInstall) {
        Write-Title "检查 OCR 环境"
        try { & (Join-Path $PSScriptRoot "install-ocr.ps1") } catch {
            Write-Warn "OCR 自动安装未完成：$($_.Exception.Message)"
            Write-Warn "应用仍可启动。文字版 PDF、PPTX、DOCX 可正常解析；扫描件 OCR 可能需要稍后手动修复。"
        }
    }

    Write-Title "启动后端服务"
    Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd '$BackendDir'; & '$BackendPython' -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    if (-not (Wait-ForUrl "http://127.0.0.1:8000/health" "后端服务")) { throw "后端服务启动失败。可能原因：依赖安装失败、端口被占用、Python 环境损坏。请运行 scripts\doctor.ps1 查看详情。" }

    Write-Title "启动前端服务"
    Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "cd '$FrontendDir'; npm run dev -- --host 127.0.0.1 --port 5173 --strictPort")
    if (-not (Wait-ForUrl "http://127.0.0.1:5173" "前端页面")) { throw "前端服务启动失败。可能原因：npm install 未成功、端口被占用、Node.js 版本过低。请运行 scripts\doctor.ps1 查看详情。" }

    Write-Title "打开浏览器"
    if (-not $NoBrowser) { Start-Process "http://127.0.0.1:5173" }

    Write-Host ""
    Write-Host "启动成功！浏览器地址：http://127.0.0.1:5173" -ForegroundColor Green
    Write-Host "使用期间请不要手动结束后台的 Python / Node.js 进程。"
    Write-Host "如需停止服务，请运行：scripts\stop-app.ps1"
    Pause-IfNeeded -NoPause:$NoPause
} catch {
    Write-Host ""
    Write-Fail "启动失败：$($_.Exception.Message)"
    Write-Host ""
    Write-Host "可尝试以下操作："
    Write-Host "1. 运行 scripts\doctor.ps1 查看诊断报告。"
    Write-Host "2. 运行 scripts\stop-app.ps1 停止旧服务后再双击 start.bat。"
    Write-Host "3. 确认已安装 Python 3.11+ 和 Node.js 18+。"
    Pause-IfNeeded -NoPause:$NoPause
    exit 1
}
