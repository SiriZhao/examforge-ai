# Windows 桌面版

运行 `scripts/build-windows.ps1` 会先构建前端，再将 `frontend/dist` 加入 PyInstaller 数据文件，输出 `dist/ExamForgeAI.exe` 和可选安装包 `dist/installer/ExamForgeAISetup-0.6.0.exe`。

桌面版使用本机工作空间、上传目录、输出目录和 OCR 缓存。前端路径兼容 `sys._MEIPASS`，启动后会在随机本地端口打开浏览器，不应出现 `Frontend build not found`。
