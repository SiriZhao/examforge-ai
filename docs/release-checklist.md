# 发布检查清单

1. 运行前端 `npm run lint`、`npm run typecheck`、`npm run test -- --run` 和 `npm run build`。
2. 运行后端 `python -m pytest`，并在可用环境中构建 Docker 与 Windows 桌面版。
3. 扫描真实 API Key、Token、`.env`、上传资料、缓存和导出文件；它们不得进入 Git。
4. 确认 `dist/ExamForgeAI.exe` 和可选安装包只作为 Release assets 上传。
5. 验证 `/api/health`、首页静态资源、匿名工作空间隔离、上传限制和导出。
6. 推送功能分支，合并 main 后创建版本 tag 与 GitHub Release。
