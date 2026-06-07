@echo off
chcp 65001 >nul
setlocal
title ExamForge AI 期末复习资料生成器

cd /d "%~dp0"

echo.
echo 正在启动 ExamForge AI 期末复习资料生成器...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-dev.ps1"

if errorlevel 1 (
  echo.
  echo 启动失败。请查看上方提示，或运行 scripts\doctor.ps1 进行诊断。
  echo.
  pause
)

endlocal
