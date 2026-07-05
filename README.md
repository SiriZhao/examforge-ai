# ExamForge AI

ExamForge AI 是面向大学生期末复习场景的资料包生成器。用户上传课件、教材、笔记、扫描试卷、往年题或图片后，系统会完成文本解析、OCR 清洗、多文件证据整合、题型反推、AI 深度整理和多格式导出，生成可直接复习、背诵、刷题和导入 Anki 的资料包。

English summary: ExamForge AI turns scattered course materials into exam-ready study packs with OCR cleanup, evidence extraction, optional LLM enhancement, mock exams, Anki cards, and Markdown / Word / PDF / Anki CSV export.

作者：[SiriZhao](https://github.com/SiriZhao)  
仓库：[SiriZhao/examforge-ai](https://github.com/SiriZhao/examforge-ai)  
当前版本：v0.4.1  
许可证：MIT License

## 核心能力

- 支持 PDF、PPTX、DOCX、Markdown、TXT、PNG、JPG、JPEG。
- 文字版 PDF 自动提取文本，扫描页按需 OCR，避免无意义逐页 OCR。
- 支持 OCR 缓存、噪声清洗、公式片段保护、坏标题过滤。
- 支持复习目标：1 天速通、3 天冲刺、7 天系统复习、重点背诵、重点刷题、整理 Anki、根据往年题抓重点、平衡模式。
- 支持考试类型：不确定、闭卷、开卷、机考、编程、实验、论文/论述、口试/展示、课程论文/报告。
- 支持详细度和输出风格：简洁、标准、详细、超详细；考前冲刺、学霸笔记、助教讲义、刷题训练、Anki 制卡。
- 支持 DeepSeek / OpenAI-compatible 模型增强，也支持无 API Key 的本地安全底稿模式。
- 支持长材料自动分块：chunk insight、证据包压缩、最终合成和 CONTEXT_TOO_LONG 自动重试。
- 支持 Markdown、DOCX、PDF、Anki CSV 下载。
- 同时支持云端 Web App 和 Windows 桌面版。

## 为什么不直接把资料发给 ChatGPT / NotebookLM？

ExamForge AI 不是普通聊天界面，而是一条期末复习资料生产线：

| 能力 | ExamForge AI | 普通大模型聊天 |
| --- | --- | --- |
| OCR 清洗 | 自动处理扫描页、噪声、缓存 | 依赖用户手动整理 |
| 多文件证据整合 | 自动合并课件、笔记、教材、往年题 | 需要反复提示 |
| 往年题题型反推 | 根据真实题干和题号结构归纳题型 | 不稳定 |
| 长材料处理 | 分块理解、chunk insight、最终合成 | 容易超上下文 |
| 复习目标定制 | 内置目标和考试类型 | 需要用户自己设计 prompt |
| 质量守门 | 检查题目、答案、Anki、乱码和导出字段 | 无内置校验 |
| 导出 | Markdown / Word / PDF / Anki CSV | 通常要复制排版 |
| 本地兜底 | 无 Key 也可生成安全底稿 | 无 |
| 双形态发布 | 云端网页 + Windows 桌面版 | 不适用 |

## 在线网页端使用教程

部署者上线后，用户打开部署链接即可使用。若当前还没有公开链接，可按下方 Docker / Render / Railway / Fly.io 教程自行部署。

网页端流程：

1. 打开部署链接。
2. 输入课程名或考试名，例如“概率论”“Python”“植物学下”。
3. 上传课件、教材、笔记、往年题、扫描 PDF 或图片。
4. 选择复习目标、考试类型、OCR 模式、详细度和输出风格。
5. 选择本地整理或 AI 深度整理。
6. 如果部署者没有配置服务端 Key，可在网页端填写自己的 DeepSeek / OpenAI-compatible API Key。
7. 点击生成。
8. 在线预览复习资料、题型分析、模拟卷、Anki 卡片和生成过程摘要。
9. 下载 Markdown、Word、PDF 或 Anki CSV。

如果不填写 API Key，系统仍会使用本地安全底稿模式生成可用资料。AI 深度整理通常能显著提升章节命名、题型归纳、模拟题和 Anki 卡片质量。

## Windows 桌面版使用教程

从 GitHub Releases 下载：

```text
ExamForgeAISetup-0.4.1.exe
```

安装后运行 ExamForge AI。桌面版适合处理更隐私的资料，默认数据目录为：

```text
%LOCALAPPDATA%\ExamForgeAI
```

桌面版仍可配置 DeepSeek / OpenAI-compatible API Key；不配置 Key 时使用本地安全底稿。

## 本地开发

```bash
git clone https://github.com/SiriZhao/examforge-ai.git
cd examforge-ai
```

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

前端开发地址通常是：

```text
http://127.0.0.1:5173
```

本地开发如需指定后端地址，可在前端环境变量中设置：

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

未设置时，生产构建会默认使用同源 `/api`。

## Docker 部署

```bash
docker build -t examforge-ai .
docker run --rm -p 8000:8000 --env-file .env.example examforge-ai
```

打开：

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/api/health
```

Docker 镜像会构建前端并由 FastAPI 托管静态页面，云端平台通过 `PORT` 环境变量指定端口。

## Render 部署

1. 打开 [Render](https://render.com) 并登录。
2. 点击 New +，选择 Web Service。
3. 连接 GitHub 仓库 `SiriZhao/examforge-ai`。
4. Environment 选择 Docker。
5. Branch 选择 `main`。
6. Root Directory 留空。
7. Health Check Path 填 `/api/health`。
8. 添加环境变量：

```text
APP_MODE=cloud
PORT=10000
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_LLM_MODEL=deepseek-v4-flash
DEFAULT_LLM_BASE_URL=https://api.deepseek.com
MAX_UPLOAD_MB=50
MAX_FILES_PER_REQUEST=10
JOB_TIMEOUT_SECONDS=600
TEMP_FILE_TTL_HOURS=24
ENABLE_RAPIDOCR=true
ENABLE_TESSERACT=false
ENABLE_CLOUD_SAFE_MODE=true
LLM_CONTEXT_BUDGET_CHARS=120000
LLM_CHUNK_CHARS=18000
LLM_CHUNK_OVERLAP_CHARS=1200
LLM_MAX_CHUNKS_PER_ROUND=8
LLM_MAX_REPAIR_CALLS=1
LLM_ENABLE_CHUNK_SUMMARY=true
LLM_ENABLE_FINAL_SYNTHESIS=true
```

如需让用户免填 Key，可额外配置：

```text
DEEPSEEK_API_KEY=你的服务端 Key
```

不要把真实 Key 写入代码或提交到 Git。

## Railway / Fly.io 部署

Railway 通常会识别根目录 Dockerfile 并构建服务；设置和 Render 类似的环境变量即可。

Fly.io 可使用：

```bash
fly launch
fly deploy
```

生产环境请配置 HTTPS、访问控制、上传限制、日志保护和成本监控。

## API Key 说明

ExamForge AI 支持两种 AI Key 模式：

1. 服务端默认 Key：部署者通过环境变量配置 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`。后端使用该 Key，但不会返回给前端。
2. 用户自带 Key：用户在网页端输入自己的 Key。后端仅用于当次请求，默认不写入服务器文件；前端若选择保存，只应保存在当前浏览器 localStorage，并提示用户。

生产环境必须使用 HTTPS 传输用户自带 Key。

## 长材料与 CONTEXT_TOO_LONG

v0.4.1 起，长材料不再轻易直接退回本地安全底稿。系统会：

1. 按文件、页面、章节、题号和自然段智能分块。
2. 为每个 chunk 生成 chunk insight，保留考点、定义、公式、题型线索、往年题题干、Anki 候选和证据片段。
3. 将 evidence pack、local_safe_draft、chunk insights、题干候选和用户设置合成为最终 AI 复习包。
4. 如果模型返回 CONTEXT_TOO_LONG，自动缩小证据包并重试最终合成。
5. 只有多次失败后，才回退本地安全底稿。

## 上传限制

默认允许：

```text
pdf, pptx, docx, md, txt, png, jpg, jpeg
```

默认拒绝：

```text
exe, bat, ps1, sh, js, html, php, py, dll, msi, zip, rar, 7z
```

默认上传配置可通过环境变量调整：

```text
MAX_UPLOAD_MB=50
MAX_FILES_PER_REQUEST=10
JOB_TIMEOUT_SECONDS=600
TEMP_FILE_TTL_HOURS=24
```

## 项目结构

```text
examforge-ai/
├─ backend/              FastAPI 后端、解析、OCR、LLM、导出
├─ frontend/             React + TypeScript 前端
├─ docs/                 部署、用户指南、安全、隐私、免责声明
├─ examples/             可公开的虚构示例材料
├─ scripts/              构建、清理、Windows 打包脚本
├─ installer/            Windows 安装包配置
├─ .github/              GitHub Actions 与模板
├─ Dockerfile            云端 Web App 镜像构建
├─ docker-compose.yml    本地 Docker 示例
├─ render.yaml           Render 示例配置
├─ fly.toml              Fly.io 示例配置
├─ ExamForgeAI.spec      PyInstaller 打包配置
├─ desktop_main.py       Windows 桌面版入口
├─ start.bat             本地启动脚本
├─ README.md
└─ LICENSE
```

## 隐私与安全

- 云端部署时，上传文件会由服务器处理。
- 使用 AI 深度整理时，材料证据可能会发送给对应 LLM 服务商。
- 用户自带 Key 默认不应存储在服务器。
- 本地桌面版更适合处理隐私敏感资料。
- 请勿上传无权处理的课程资料、考试资料或包含个人隐私的文件。
- 公共部署建议增加 HTTPS、登录、限流、任务队列、成本监控和滥用防护。

更多文档：

- [docs/user-guide.md](docs/user-guide.md)
- [docs/cloud-deployment.md](docs/cloud-deployment.md)
- [docs/windows-desktop.md](docs/windows-desktop.md)
- [docs/security.md](docs/security.md)
- [docs/privacy.md](docs/privacy.md)
- [docs/disclaimer.md](docs/disclaimer.md)
- [docs/release-checklist.md](docs/release-checklist.md)

## 免责声明

- 本项目生成内容仅供学习和复习辅助。
- 不保证押题准确，也不保证生成内容完全正确。
- 用户应自行核对课程材料、教材和教师要求。
- 本项目不鼓励作弊、泄露考试内容或违反学校规定。
- 上传和使用资料前，请确认拥有合法权限。

## 依赖与商用提示

本项目使用 FastAPI、React、PyInstaller、文档解析、OCR 和 LLM API 相关依赖。项目代码采用 MIT License；商用部署前，请自行审查第三方依赖许可证、LLM 服务条款、学校/机构规定和当地法律法规。

## License

MIT License. See [LICENSE](LICENSE).
