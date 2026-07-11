# Windows 桌面版打包

在 Windows 构建机的仓库根目录运行：

```powershell
.\scripts\build-windows.ps1
```

脚本会构建 `frontend/dist`、运行测试、通过 PyInstaller 打包 FastAPI 与前端静态资源，并在安装 Inno Setup 时生成安装包。

预期产物：

```text
dist/ExamForgeAI.exe
dist/installer/ExamForgeAISetup-0.6.0.exe
```

桌面版数据保存在 `%LOCALAPPDATA%\ExamForgeAI`。前端资源打入 `frontend/dist`，运行时通过 `sys._MEIPASS` 查找；若浏览器未自动打开，请查看 `%LOCALAPPDATA%\ExamForgeAI\logs\desktop.log` 的本地 URL。发布时只把 EXE 或安装包作为 GitHub Release assets 上传，不提交到 main 分支。
