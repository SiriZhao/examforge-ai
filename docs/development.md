# 开发说明

RecallForge AI 使用 React/Vite 前端与 FastAPI 后端。开发模式下，前端通过 `VITE_API_BASE_URL` 指向后端；未设置该变量时使用同源 `/api`。

```powershell
cd frontend
npm install
npm run lint
npm run typecheck
npm run test -- --run
npm run build

cd ..\backend
python -m pip install -r requirements.txt
python -m pytest
```

不要提交 `.env`、SQLite 数据库、上传资料、缓存、导出文件、`dist`、`build`、虚拟环境或 `node_modules`。本地工作空间和临时文件都应保存在运行时目录。
