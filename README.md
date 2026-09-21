# RecallForge AI

AI-native exam review and active learning workspace for university courses.

RecallForge AI 是面向大学课程学习与期末复习的 AI 原生复习工作台：把课程材料转化为有证据依据、可主动回忆、可练习和可导出的学习成果。

当前版本：**v0.6.0**

Repository: [github.com/SiriZhao/recallforge-ai](https://github.com/SiriZhao/recallforge-ai)

## What is RecallForge AI?

传统的 AI 总结通常只回答“材料讲了什么”，却不一定帮助你准备考试。RecallForge AI 关注从材料理解到复习行动的完整闭环：

- active recall（主动回忆）
- knowledge reconstruction（知识重建）
- weakness detection（薄弱点识别）
- adaptive practice（适应性练习）
- exam-oriented review（面向考试的复习）
- evidence grounding（基于原始材料的证据约束）

## Core capabilities

- 按课程、考试日期、考试形式和学习目标建立复习项目。
- 解析并诊断多份课程材料，区分课程纲要、课件、教材、笔记、往年题、答案和错题等角色。
- LLM-first 分阶段生成：材料分块与理解 → Course Model → Study Blueprint → 单元草稿 → 全局合成，并保留来源与覆盖诊断。
- 生成知识重点地图、复习讲义、往年题分析、题型攻略、主动回忆题、闪卡、易错点、冲刺计划和模拟卷。
- 提供局部重试/修复、生成任务状态、报告版本保存，以及 Markdown、DOCX、PDF 和 Anki CSV 导出。
- 提供本地 OCR、证据提取、质量检查和离线基础整理作为安全基线与 fallback。

## How it works

```text
Course Materials
      ↓
Parse & Understand
      ↓
Evidence / Knowledge Reconstruction
      ↓
LLM Reasoning and Study Planning
      ↓
Recall / Practice / Weakness Detection
      ↓
Exam Simulation
      ↓
Evidence-grounded Markdown / DOCX / PDF / Anki output
```

## LLM-first architecture

LLM 模式是当前主要产品路径。用户通过 BYOK 配置 provider、Base URL、模型和 API Key；后端以 OpenAI-compatible 请求方式调用模型，并在分阶段 pipeline 中约束模型引用用户材料、保留 unresolved chunks 和覆盖诊断。

当前代码内置/兼容的 provider 路径包括 DeepSeek、OpenAI，以及可配置 Base URL 的其他 OpenAI-compatible 服务。具体模型名称由用户配置，不在项目中硬编码。

API Key 默认只保存在当前浏览器 `localStorage`，不会写入工作空间数据库、日志或 Git。未配置 LLM 时，系统才使用基础离线整理；离线逻辑用于 fallback、验证、证据提取和基本解析，不是主要 intelligence engine。

## Supported materials

- PDF（包括可提取文本的 PDF；扫描页可由 OCR 处理）
- PPTX
- DOCX
- Markdown
- TXT
- PNG / JPG / JPEG 图片

OCR provider 可按环境使用 RapidOCR、本地 Tesseract，或已配置的外部 OCR/视觉 provider。OCR 的可用性取决于本机依赖和 provider 配置。

## Main workflows

### Knowledge reconstruction

从多份材料提取章节、概念、公式、定义、来源引用和课程范围，形成 Course Model 与 Study Blueprint。

### Active recall and weakness detection

围绕重点和易错点生成回忆题、闪卡、检查点和练习建议，并在报告中保留覆盖与质量诊断。

### Adaptive practice and exam simulation

结合课程目标、往年题和考试形式生成题型攻略、练习集与模拟卷；生成内容仍需根据原始材料和教师要求复核。

### Study pack generation

报告可按模块查看、局部修复并导出为 Markdown、DOCX、PDF 或 Anki CSV。

## Quick start

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL="http://127.0.0.1:8000/api"
npm run dev
```

打开 Vite 输出的本地地址（通常是 `http://localhost:5173`）。

### Docker

```bash
docker build -t recallforge-ai:0.6.0 .
docker run --rm -p 8000:8000 --env-file .env.example recallforge-ai:0.6.0
```

### Windows desktop packaging

```powershell
.\scripts\build-windows.ps1
```

脚本会构建前端并使用 PyInstaller 生成桌面版。现有 `ExamForgeAI.exe` 文件名和 `%LOCALAPPDATA%\ExamForgeAI` 数据目录属于兼容性标识，暂不改动，以避免破坏已有安装和用户数据。

## LLM configuration

在应用的模型设置中填写 Provider、Base URL、模型名称和 API Key。默认 provider 是 DeepSeek；OpenAI-compatible provider 可通过自定义 Base URL 使用。公共部署必须使用 HTTPS，并应关闭服务端默认 Key（`ENABLE_SERVER_LLM_KEY=false`），除非你明确理解其共享风险。

材料只有在你选择 LLM/OCR provider 并发起请求时才会发送到相应外部服务。请先确认课程资料的授权范围和 provider 的数据政策。

## Data and privacy

- 本地/桌面模式将工作空间、上传文件、缓存和报告保存在项目配置的本地目录。
- 云端模式使用匿名 `workspace_id` 与 secret 进行资源隔离，并按 `TEMP_FILE_TTL_HOURS` 清理临时文件。
- API Key 默认保存在浏览器 `localStorage`；删除浏览器站点数据即可删除该配置。
- 可删除工作空间或本地运行目录中的上传/输出数据；不要把 `workspace.db`、上传材料、缓存或 `.env` 提交到 Git。
- 外部模型输出仅作学习辅助，必须核对原始材料与教师要求。

## Project structure

```text
backend/      FastAPI API、解析/OCR、LLM pipeline、存储、导出和测试
frontend/     React/Vite workspace UI、任务状态和报告查看器
docs/         配置、隐私、部署、解析、OCR、导出和开发文档
examples/     示例课程材料和输出
installer/    Windows 安装器配置与版本信息
scripts/      本地开发、诊断、测试和 Windows 构建脚本
```

## Development and tests

```powershell
python -m pytest backend
cd frontend
npm run test -- --run
npm run build
npm run lint
```

也可以在仓库根目录运行 `./scripts/test-all.ps1`，一次执行后端测试、前端测试和前端构建。

## Roadmap

- richer multimodal understanding
- stronger active-recall planning
- adaptive difficulty and weakness modelling
- more export formats
- evaluation and regression framework
- skill/agent integrations

## Project evolution

RecallForge AI evolved from the earlier **ExamForge AI** / **Campus AI Workspace** iterations. Those names remain only in historical release notes and compatibility identifiers; the current product and repository branding is RecallForge AI.

## License

[MIT License](LICENSE) © SiriZhao
