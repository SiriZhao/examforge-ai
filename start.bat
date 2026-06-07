@echo off
chcp 65001 >nul
setlocal
title ExamForge AI
cd /d "%~dp0"

echo.
echo Starting ExamForge AI...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-dev.ps1"

if errorlevel 1 (
  echo.
  echo Startup failed. Please run scripts\doctor.ps1 to diagnose the problem.
  echo.
  pause
)

endlocal
