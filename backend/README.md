# RecallForge AI 后端

FastAPI 后端提供匿名工作空间、项目级上传、文档解析、OCR、长文档分块、复习资料生成和导出。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

主要健康检查为 `GET /api/health` 和 `GET /api/ready`。用户 API Key 不写入数据库或日志；未配置模型时仍可生成本地安全底稿。
