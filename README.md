# ExamForge AI

面向大学生期末复习的 AI 复习资料生成器。上传课件、教材、笔记、扫描试卷和往年题，生成可导出的复习资料包、模拟卷、Anki 卡片和考前冲刺计划。

ExamForge AI turns messy course materials into structured exam-ready study packs with OCR cleanup, evidence extraction, optional LLM enhancement, and Markdown / Word / PDF / Anki CSV export.

Author: [SiriZhao](https://github.com/SiriZhao)  
Repository: [SiriZhao/examforge-ai](https://github.com/SiriZhao/examforge-ai)

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![React](https://img.shields.io/badge/React-19-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178c6)
![Docker](https://img.shields.io/badge/Docker-supported-2496ed)
![Windows](https://img.shields.io/badge/Windows-supported-0078d4)

## 为什么做这个项目

期末复习材料往往不是一个干净的知识库，而是一堆分散的 PPT、PDF、教材截图、课堂笔记、扫描试卷和往年题。普通大模型聊天可以回答问题，但用户仍然需要手动整理 OCR、提炼重点、归纳题型、排版导出和制作 Anki。

ExamForge AI 的目标不是替代学习，而是提供一条完整的期末复习资料生产线：

1. 解析多种课程资料。
2. 清洗 OCR 和文本噪声。
3. 构建多文件证据包。
4. 根据往年题和题干线索反推题型。
5. 让 AI 深度整理章节、考点、模拟题和 Anki。
6. 进行质量校验与本地安全底稿兜底。
7. 导出 Markdown、Word、PDF 和 Anki CSV。

## 核心功能

- 支持 PDF、PPTX、DOCX、Markdown、TXT、PNG、JPG、JPEG。
- 支持文字版 PDF 直接提取，扫描件按需 OCR。
- 支持 OCR 缓存、文本清洗、公式碎片过滤和坏标题过滤。
- 支持多文件证据整合，区分课件、笔记、教材、往年题和扫描材料。
- 支持复习目标：1 天速通、3 天冲刺、7 天系统复习、重点背诵、重点刷题、Anki 整理、根据往年题抓重点、平衡模式。
- 支持考试类型：闭卷、开卷、机考、编程、实验、论文/论述、口试/展示、课程论文/报告。
- 支持题型反推：根据 OCR、往年题、真实题干和材料结构自动归纳题型。
- 支持 AI 深度整理：DeepSeek 或 OpenAI-compatible 模型。
- 支持本地整理模式：无需 API Key，也能生成可用安全底稿。
- 支持重新优化报告：无需重新 OCR，可按背诵、刷题、Anki、简洁、详细等方向优化。
- 支持 Markdown、DOCX、PDF 和 Anki CSV 导出。
- 支持云端 Web App 和 Windows 桌面版双形态发布。

## 与直接使用 ChatGPT / NotebookLM 的区别

| 能力 | ExamForge AI | 普通大模型聊天 |
| --- | --- | --- |
| OCR 清洗 | 自动处理 | 依赖上传质量 |
| 多文件证据整合 | 内置 | 需要手动提示 |
| 往年题题型反推 | 内置 | 不稳定 |
| 复习目标和考试类型 | 内置 | 需要反复提示 |
| 模拟卷与答案解析 | 自动生成并校验 | 需要手动整理 |
| Anki CSV 导出 | 支持 | 通常需要手动制作 |
| Word / PDF / Markdown 导出 | 支持 | 需要复制排版 |
| 本地安全底稿 | 支持 | 无 |
| 云端与桌面双模式 | 支持 | 无 |

## 快速开始

### 方式一：云端 Web App

如果已经有部署好的实例，打开部署链接即可使用。

自行部署推荐使用 Docker：

```bash
docker build -t examforge-ai .
docker run --rm -p 8000:8000 --env-file .env.example examforge-ai
```

然后打开：

```text
http://127.0.0.1:8000
```

健康检查：

```text
http://127.0.0.1:8000/api/health
```

### 方式二：Windows 桌面版

从 GitHub Releases 下载并安装：

```text
ExamForgeAISetup-0.4.0.exe
```

桌面版更适合处理隐私敏感资料或离线使用。运行时数据默认存储在：

```text
%LOCALAPPDATA%\ExamForgeAI
```

### 方式三：本地开发

```bash
git clone https://github.com/SiriZhao/examforge-ai.git
cd examforge-ai
```

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

默认开发地址：

```text
http://127.0.0.1:5173
```

## AI 与 API Key 配置

- 本地整理模式无需 API Key。
- AI 深度整理建议配置 DeepSeek 或 OpenAI-compatible API。
- DeepSeek 示例：
  - Provider: `deepseek`
  - Base URL: `https://api.deepseek.com`
  - Model: `deepseek-v4-flash`，或替换为你实际可用的模型。
- 不要把真实 API Key 提交到 Git。
- 云端部署可通过平台 Secret 配置服务端默认 Key，也可以让用户在浏览器中输入自己的 Key。
- 用户自带 Key 应通过 HTTPS 传输；服务端默认 Key 不会返回给前端。

## 云端部署

项目支持 Docker 单体部署：FastAPI 同时提供 API、上传处理、生成任务、下载接口和前端静态页面。

常用平台：

- Docker
- Render
- Railway
- Fly.io

详细说明见 [docs/cloud-deployment.md](docs/cloud-deployment.md) 和 [docs/deployment.md](docs/deployment.md)。

关键环境变量示例见 [.env.example](.env.example)。

## 项目结构

```text
examforge-ai/
├── backend/              # FastAPI 后端、文档解析、OCR、LLM、导出
├── frontend/             # React + TypeScript 前端
├── docs/                 # 部署、隐私、安全、免责声明和打包文档
├── examples/             # 可公开的虚构示例材料
├── scripts/              # 测试、构建和打包脚本
├── installer/            # Windows 安装包配置和图标
├── .github/              # Issue 模板和 GitHub Actions
├── Dockerfile            # 云端 Web App 镜像构建
├── docker-compose.yml    # 本地 Docker 运行示例
├── render.yaml           # Render 部署示例
├── fly.toml              # Fly.io 部署示例
├── ExamForgeAI.spec      # PyInstaller 桌面版打包配置
├── desktop_main.py       # Windows 桌面版启动入口
├── start.bat             # 本地开发启动脚本
├── README.md
└── LICENSE
```

## 示例材料

`examples/` 目录只包含虚构 demo，不包含真实课程资料、真实试卷或个人文件。可以用这些文件做本地冒烟测试：

- [examples/demo_course_material.md](examples/demo_course_material.md)
- [examples/demo_past_exam.md](examples/demo_past_exam.md)
- [examples/demo_output.md](examples/demo_output.md)

## 隐私与安全

- 本地桌面版更适合处理隐私敏感资料。
- 云端部署时，上传文件会由服务器处理。
- 使用 LLM 时，材料证据可能会发送给对应模型服务商。
- 用户应确保自己有权处理、上传和分析相关资料。
- 不要提交 `.env`、真实 API Key、真实课程资料、真实上传文件或真实生成报告。
- 公共云端部署建议增加 HTTPS、访问控制、限流、监控、成本控制和滥用防护。

更多信息：

- [docs/privacy.md](docs/privacy.md)
- [docs/security.md](docs/security.md)
- [docs/disclaimer.md](docs/disclaimer.md)
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)

## 免责声明

- 生成内容仅供学习和复习辅助。
- 不保证押题准确，不保证生成内容完全正确。
- 用户应自行核对课程材料、教材和教师要求。
- 不鼓励作弊、泄露考试内容或违反学校规定。
- 上传和使用资料前，请确认拥有合法权限。

## Roadmap

- 更稳定的题型反推和往年题加权。
- 更强的自测模式和错题本。
- 更好的在线 Demo、截图和演示数据。
- 云端任务队列、多用户隔离和访问限流。
- 更细粒度的导出模板和 Anki 制卡策略。

## English Summary

ExamForge AI is an open-source exam preparation assistant that turns scattered course materials into structured study packs. It supports OCR cleanup, multi-file evidence integration, past-exam question type inference, mock exams, Anki CSV export, quality checks, and optional LLM enhancement. It can run as a cloud web app or as a Windows desktop app.

## License

MIT License. See [LICENSE](LICENSE).
