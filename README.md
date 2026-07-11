# CampusForge

Build Smarter. Learn Better.

CampusForge 是面向大学生的一站式 AI 学习与校园效率平台。当前仓库由 ExamForge AI 升级而来，保留期末复习资料包生成能力，并在 v0.5.0 引入 Web SaaS 架构基座：GitHub Pages 前端、FastAPI 云端后端、Supabase 认证/数据库/存储迁移、Stripe 计费配置、Windows 桌面客户端和发布流水线。

> 当前版本：v0.5.0
> 仓库：<https://github.com/SiriZhao/examforge-ai>
> 作者：SiriZhao
> License：MIT

## 当前可用能力

- 上传 PDF、PPTX、DOCX、Markdown、TXT、PNG、JPG、JPEG。
- OCR 清洗、文本抽取、多文件证据整合。
- 长材料自动分块、chunk insight、最终合成，降低 `CONTEXT_TOO_LONG` 失败率。
- 本地安全底稿，无 API Key 时也能生成可导出的基础资料。
- 可选 DeepSeek / OpenAI-compatible AI 深度整理。
- 复习目标、考试类型、详细度、输出风格。
- Markdown、DOCX、PDF、Anki CSV 导出。
- FastAPI 同源托管前端，支持 Docker 云端部署。
- Windows 桌面 EXE 打包。
- GitHub Pages 前端部署工作流。
- Supabase / Stripe 配置和数据库迁移基座。

## 尚需部署者配置的能力

以下能力需要 Supabase、Stripe、云平台和 GitHub 账户权限，不会在本地凭空生效：

- Supabase 项目创建、Auth Redirect URL 配置、数据库迁移执行、Storage Bucket 创建。
- Stripe Product / Price / Webhook Secret 配置。
- 后端云服务部署 URL。
- GitHub Pages 启用 GitHub Actions 部署。
- GitHub Actions Variables / Secrets。
- GitHub Release 上传资产。

详细清单见 [docs/MANUAL_ACTIONS_REQUIRED.md](docs/MANUAL_ACTIONS_REQUIRED.md)。

## 网页端使用流程

1. 打开部署后的 CampusForge 网页。
2. 输入课程或考试名称。
3. 上传课件、教材、笔记、往年题或扫描图片。
4. 选择复习目标、考试类型、详细度和输出风格。
5. 选择本地整理模式，或配置 DeepSeek / OpenAI-compatible API Key 开启 AI 深度整理。
6. 点击生成。
7. 在线预览复习资料包。
8. 下载 Markdown / Word / PDF / Anki CSV。

如果部署者没有配置服务端 API Key，用户可以在网页端填写自己的 API Key。用户 Key 默认只随请求临时发送，不写入服务器文件；如果选择浏览器保存，应只保存在当前浏览器。

## 为什么不直接发给 ChatGPT / NotebookLM

| 能力 | CampusForge | 普通大模型聊天 |
| --- | --- | --- |
| OCR 清洗 | 自动处理扫描件和噪声 | 依赖上传质量 |
| 多文件证据整合 | 按文件、题干、公式、定义组织证据 | 需要反复提示 |
| 长材料处理 | 分块理解、chunk insight、最终合成 | 容易超上下文 |
| 往年题题型反推 | 提取题型线索并指导模拟卷 | 不稳定 |
| 导出 | Markdown / DOCX / PDF / Anki CSV | 通常要手动排版 |
| 质量守门 | 解析兜底、修复、回退安全底稿 | 用户自行判断 |
| 部署形态 | 云端 Web + Windows EXE | 仅聊天界面 |

## 本地开发

```powershell
git clone https://github.com/SiriZhao/examforge-ai.git
cd examforge-ai

cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

cd ..\frontend
npm install
$env:VITE_API_BASE_URL="http://127.0.0.1:8000/api"
npm run dev
```

访问 <http://localhost:5173>。

## Docker 云端部署

```bash
docker build -t campusforge:0.5.0 .
docker run --rm -p 8000:8000 --env-file .env.example campusforge:0.5.0
```

访问：

- <http://127.0.0.1:8000>
- <http://127.0.0.1:8000/api/health>

生产环境必须配置 HTTPS、CORS、存储目录、上传限制和必要密钥。

## Render 部署

1. 登录 <https://render.com>。
2. New + → Web Service。
3. 连接 `SiriZhao/examforge-ai`。
4. Environment 选择 Docker。
5. Branch 选择 `main`。
6. Health Check Path 填 `/api/health`。
7. 设置环境变量：

```text
APP_MODE=cloud
APP_NAME=CampusForge
APP_VERSION=0.5.0
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
LLM_ENABLE_CHUNK_SUMMARY=true
LLM_ENABLE_FINAL_SYNTHESIS=true
```

可选服务端 AI Key：

```text
DEEPSEEK_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
```

## GitHub Pages 前端部署

本仓库包含 `.github/workflows/deploy-pages.yml`。GitHub Pages 只部署前端静态文件，后端必须部署到持续运行的云平台。

需要在 GitHub 仓库中配置：

- Settings → Pages → Source 选择 GitHub Actions。
- Repository Variables：
  - `VITE_API_BASE_URL`
  - `VITE_SUPABASE_URL`
  - `VITE_STRIPE_PUBLISHABLE_KEY`
- Repository Secrets：
  - `VITE_SUPABASE_ANON_KEY`

最终项目站点地址按仓库自动计算：`https://<owner>.github.io/<repo>/`。

## Windows 桌面版

```powershell
.\scripts\build-windows.ps1
```

成功后生成：

- `dist/CampusForge.exe`
- `dist/installer/CampusForgeSetup-0.5.0.exe`，如果本机安装了 Inno Setup。

桌面版不应内置服务器密钥。用户可输入自己的 API Key，或连接已配置服务端 Key 的云端后端。

## Supabase 与 Stripe

数据库迁移位于：

```text
supabase/migrations/0001_campusforge_saas.sql
```

该迁移建立 profiles、projects、uploaded_files、ai_tasks、usage、credits、subscriptions、payment_events 等基础表，并启用 RLS。执行前请在测试项目验证。

Stripe 相关密钥只允许放在后端环境变量：

```text
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PUBLISHABLE_KEY=
```

不得将 `STRIPE_SECRET_KEY`、`SUPABASE_SERVICE_ROLE_KEY` 或 AI API Key 放入前端、EXE 或 GitHub Pages 构建输出。

## 长材料处理

v0.5.0 继续保留 v0.4.1 的长上下文策略：

- 字符预算保护。
- 智能分块。
- chunk insight。
- final synthesis。
- `CONTEXT_TOO_LONG` 自动降级重试。
- 多次失败后才回退本地安全底稿。

系统会优先保留往年题题干、题型线索、公式、定义、例题、代码、易错点、PPT 标题和用户设置。

## 隐私说明

- 云端部署时，用户上传文件会由部署者服务器处理。
- 如果启用服务端 AI Key，材料可能会发送给对应 LLM 服务商。
- 用户自带 API Key 默认不写入服务器文件。
- 本地桌面版更适合处理隐私敏感资料。
- 请勿上传无权处理的课程资料、考试资料或含个人隐私的文件。

更多内容见 [docs/privacy.md](docs/privacy.md)。

## 免责声明

- 生成内容仅供学习和复习辅助。
- 不保证押题准确，不保证内容完全正确。
- 用户应自行核对课程材料、教师要求和学校规定。
- 不鼓励作弊、泄露考试内容或违反学校规定。
- 自部署者需自行承担服务器成本、API 成本和数据合规责任。

更多内容见 [docs/disclaimer.md](docs/disclaimer.md)。

## 版本与发布

- 当前版本：v0.5.0
- Release tag：`v0.5.0`
- Release title：`CampusForge v0.5.0`

发布检查见 [docs/release-checklist.md](docs/release-checklist.md)。
