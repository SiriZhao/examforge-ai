# 云端部署

RecallForge AI v0.6.0 可以作为无需注册的匿名复习项目服务运行。用户在浏览器获得随机工作空间 ID 与 secret；服务端不配置默认模型 Key。

```bash
docker build -t recallforge-ai:0.6.0 .
docker run --rm -p 8000:8000 --env-file .env.example -v examforge_data:/data recallforge-ai:0.6.0
```

生产环境设置 `APP_MODE=cloud`、`APP_VERSION=0.6.0`、`PUBLIC_BASE_URL`、严格 `CORS_ORIGINS`、上传大小/数量限制、TTL 和持久化 `/data`。设置 `ENABLE_SERVER_LLM_KEY=false`，不要在平台环境变量中放开发者 DeepSeek Key。

Render：使用根目录 Dockerfile，Health Check 为 `/api/health`，挂载 `/data` 持久盘。Railway/Fly.io 同理。公开部署应使用 HTTPS；敏感资料建议桌面版。
