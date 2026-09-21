# RecallForge AI 前端

React + Vite 前端实现无注册的期末复习项目流程：复习设置、资料上传和角色标记、资料诊断、分块生成、复习包预览与导出。

```powershell
npm install
npm run dev
npm run lint
npm run test -- --run
npm run build
```

未设置 `VITE_API_BASE_URL` 时，前端使用同源 `/api`，适合 Docker 和 Windows 桌面版。
