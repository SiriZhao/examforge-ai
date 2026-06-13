# ExamForge AI 后端

这是 ExamForge AI｜期末复习资料生成器的 FastAPI 后端服务，负责上传文件、解析文本、执行 OCR、生成复习报告和导出文件。

## 启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 主要接口

- `GET /health`
- `POST /upload`
- `POST /parse`
- `POST /generate-review`
- `POST /api/analyze/`
- `POST /api/export/`

应用启动时会创建 `uploads/` 和 `outputs/`。这些目录中的真实上传文件和生成文件不会提交到 Git，仓库中只保留 `.gitkeep`。

## 解析请求示例

```json
{
  "files": ["saved-file-name.pdf"],
  "ocr_config": {
    "provider": "local_tesseract",
    "language": "chi_sim+eng"
  }
}
```

## 生成复习资料请求示例

```json
{
  "files": ["saved-file-name.pdf"],
  "export_format": "md",
  "title": "高数期末冲刺资料",
  "ocr_config": {
    "provider": "local_tesseract",
    "language": "chi_sim+eng"
  },
  "llm_config": {
    "enabled": false
  }
}
```

支持导出：

- `md`
- `docx`
- `pdf`

未提供大模型 API Key 时，后端会生成本地安全底稿。
