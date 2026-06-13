# ExamForge AI｜期末复习资料生成器

把课件、教材、笔记、扫描试卷和往年题，一键整理成可直接复习的资料包。

Turn lecture slides, textbooks, notes, scanned papers, and past exams into exam-ready study packs.

作者：SiriZhao  
GitHub：[https://github.com/SiriZhao](https://github.com/SiriZhao)

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![React](https://img.shields.io/badge/React-19-61dafb)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178c6)
![Windows](https://img.shields.io/badge/Windows-supported-0078d4)
![Release](https://img.shields.io/badge/release-planned-orange)
![Stars](https://img.shields.io/badge/stars-welcome-yellow)

> 当前截图待补充。正式发布前建议补充首页、生成结果、高频考点、模拟卷和大模型设置页截图。

## 中文介绍

ExamForge AI 是一个面向大学生期末复习场景的本地 AI 复习资料生成工具。它不是普通的文档问答机器人，而是围绕“期末前如何快速整理复习材料”这一具体场景，帮助用户从课程资料中提取重点、分析高频考点、生成模拟题和记忆卡片。

它的默认本地整理模式无需 API Key，可以在本地完成基础复习资料生成；如果你希望获得更自然、更完整的表达，也可以选择接入大模型服务进行增强。项目支持 PPTX、PDF、DOCX、Markdown、图片和扫描版试卷，并可导出 Markdown、Word、PDF 与 Anki CSV。

## English Introduction

ExamForge AI is an open-source local exam preparation assistant for students. It transforms messy course materials into structured study packs, including chapter summaries, high-frequency topics, priority rankings, mock exams, flashcards, and sprint plans.

It is not a generic document chatbot. ExamForge AI is built for final-week exam preparation, works locally by default, supports optional LLM providers, and is designed for lecture slides, notes, textbooks, scanned papers, and past exams.

## 为什么做这个项目 / Why ExamForge AI

期末前的资料通常不是一个干净的知识库，而是一堆分散的 PPT、教材截图、课堂笔记、老师划重点、扫描试卷和往年题。很多学生真正需要的不是继续和文档聊天，而是尽快得到一份可以直接开始复习的资料包。

ExamForge AI 的目标是把这些零散材料整理成更可执行的复习输出：先看哪些章节、哪些考点出现频率高、可以练哪些题、最后几天怎么安排。

Most AI document tools answer questions. ExamForge AI focuses on producing structured review outputs.

## v0.3.0 新能力

- 复习目标选择：1 天速通、3 天冲刺、7 天系统复习、重点背诵、重点刷题、Anki 整理、往年题抓重点和平衡模式。
- 考试类型选择：闭卷、开卷、机考、编程、实验、论文/论述、口试/展示、课程论文/报告。
- 题型反推：结合 OCR、往年题、文件类型和题干线索，自动总结真实题型，不强制套固定题型库。
- 生成质量评分：展示资料完整度、考点覆盖度、模拟题质量、Anki 可用性、导出就绪度和证据整合度。
- 生成过程摘要：展示文件处理、PDF 文本层、OCR、缓存、证据块、题型线索、AI 调用和回退状态。
- 重新优化报告：无需重新上传、OCR 或解析文件，即可按背诵、刷题、Anki、速通、精简或模拟卷训练优化当前报告。
- 更强 Anki 卡片和模拟卷：卡片支持类型、优先级、来源提示；模拟题支持关联主题和 source hint。

## ExamForge AI 与普通大模型聊天的区别

| 能力 | ExamForge AI | 普通大模型聊天 |
| --- | --- | --- |
| OCR 清洗 | 自动处理 | 依赖用户上传质量 |
| 多文件证据整合 | 支持 | 需要手动说明 |
| 往年题题型反推 | 支持 | 不稳定 |
| 复习目标定制 | 支持 | 需要反复提示 |
| Anki CSV 导出 | 支持 | 通常需要手动整理 |
| Word/PDF 导出 | 支持 | 需要复制排版 |
| 质量评分 | 支持 | 无 |
| 本地安全底稿 | 支持 | 无 |

## 核心功能 / Features

| 功能 | 中文说明 | English |
|---|---|---|
| 多格式上传 | 支持 PPTX、PDF、DOCX、Markdown、PNG、JPG、JPEG 等课程材料。 | Upload slides, PDFs, documents, Markdown notes, and images. |
| 扫描件 OCR | 支持图片和扫描试卷文本识别，可配置本地或第三方 OCR。 | Extract text from scanned papers and images with configurable OCR providers. |
| 章节重点总结 | 从课程资料中整理章节摘要、关键词、公式、复习建议。 | Generate chapter summaries, keywords, formulas, and study suggestions. |
| 高频考点分析 | 自动识别更像往年题的材料，并统计重复出现的题型和关键词。 | Detect past-exam-like materials and summarize recurring topics and question types. |
| 章节优先级排序 | 综合资料出现频率、往年题频率和题型权重，输出 0-100 重要度。 | Rank chapters with priority scores based on material frequency and exam signals. |
| 模拟卷生成 | 按选择题、填空题、简答题、论述题生成模拟卷，并附参考答案。 | Generate mock exams with multiple question types and reference answers. |
| Anki 卡片导出 | 从高频考点和名词解释生成 CSV 卡片，字段为 `Front, Back, Tags`。 | Export Anki-compatible CSV flashcards from key topics and definitions. |
| Markdown / Word / PDF 导出 | 支持将复习报告导出为 Markdown、Word 和 PDF。 | Export study packs as Markdown, Word, and PDF files. |
| 本地运行 | 默认在本机启动前后端服务，本地整理模式无需 API Key。 | Run locally; local organizing mode works without an API key. |
| 可选大模型增强 | 可通过配置接入 OpenAI 兼容接口或自定义服务增强生成质量。 | Optionally connect LLM providers for higher-quality generation. |

## 软件截图 / Screenshots

> 当前截图待补充。正式发布前建议补充首页、生成结果、高频考点、模拟卷和大模型设置页截图。

| 页面 | 状态 |
|---|---|
| 首页 / Home | 待补充 |
| 生成结果 / Report | 待补充 |
| 高频考点 / Topics | 待补充 |
| 模拟卷 / Mock Exam | 待补充 |
| 大模型设置 / LLM Settings | 待补充 |

## 快速开始 / Quick Start

### Windows 双击启动

普通用户可以直接双击根目录下的：

```powershell
.\start.bat
```

启动脚本会检查 Python、Node.js、端口占用和依赖安装情况，并打开本地页面。

### 开发环境手动启动

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端：

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

浏览器打开：

```text
http://127.0.0.1:5173
```

### 一键开发启动脚本

```powershell
.\scripts\start-dev.ps1
```

环境诊断：

```powershell
.\scripts\doctor.ps1
```

## 使用示例 / Try with Demo Files

项目提供了虚构课程示例，适合 GitHub 展示和本地测试，不包含真实课程版权内容：

- `examples/demo_course_material.md`
- `examples/demo_past_exam.md`
- `examples/demo_output.md`

你可以启动应用后上传 `examples` 目录中的 demo 文件，观察章节重点、高频考点、模拟卷和 Anki 卡片的生成效果。

## 支持的文件类型 / Supported Files

| 类型 | 扩展名 | 说明 |
|---|---|---|
| 课件 | `.pptx` | 解析幻灯片文字内容。 |
| 文档 | `.pdf`, `.docx`, `.md` | 解析教材摘录、课堂笔记、复习资料。 |
| 图片 | `.png`, `.jpg`, `.jpeg` | 可配合 OCR 识别扫描件或拍照试卷。 |
| 往年题 | `.pdf`, `.docx`, `.md`, 图片 | 系统会根据文件名和内容特征判断是否更像往年试卷。 |

## OCR Providers

默认情况下，文字版 PDF、PPTX、DOCX 和 Markdown 不依赖 OCR。处理扫描试卷或图片时，可以选择 OCR Provider：

| Provider | 用途 | 备注 |
|---|---|---|
| Local Tesseract | 本地 OCR | 需要本机安装 Tesseract 或准备对应语言数据。 |
| RapidOCR | 本地 OCR | 依赖 `rapidocr_onnxruntime`。 |
| Baidu OCR | 云 OCR | 需要自行配置百度 OCR 凭据。 |
| OpenAI Vision | 视觉模型 OCR | 需要兼容的 API Key 和接口地址。 |
| Custom API | 自定义 OCR | 适合接入学校或个人部署的 OCR 服务。 |

OCR 是可选能力。没有 OCR 时，软件仍可处理文字版课程材料。

## LLM Providers

本地整理模式无需 API Key，适合先快速生成本地安全底稿。  
如果需要更自然的总结表达、更完整的题目解释，可以在高级设置中配置 OpenAI 兼容接口或自定义大模型服务。

建议通过环境变量或本地配置传入密钥，不要把 API Key 提交到 GitHub。

```powershell
copy .env.example .env
```

## 大模型增强说明 / LLM Enhancement

ExamForge AI 默认支持本地整理模式，无需 API Key，也可以本地生成基础复习资料。  
如果你希望得到更系统、更自然、更接近人工整理的复习资料，可以开启大模型增强。

大模型增强可以提升：

- 章节总结质量
- 高频考点归纳
- 章节优先级解释
- 模拟题质量
- Anki 卡片质量
- 考前冲刺计划系统性

DeepSeek 推荐配置：

- Provider：DeepSeek
- Base URL：`https://api.deepseek.com`
- Model：`deepseek-v4-flash`

兼容说明：`deepseek-chat` 和 `deepseek-reasoner` 作为旧兼容模型名保留。如果你已经手动填写这些模型名，程序不会强制覆盖。

配置步骤：

1. 打开高级设置
2. 启用大模型增强
3. 选择服务商
4. 填写 API Key、Base URL 和模型名称
5. 点击“测试大模型连接”
6. 连接成功后重新生成

隐私提醒：使用云端大模型或云端 OCR 时，上传资料内容可能会发送给对应服务商处理。请勿上传敏感个人信息、无授权资料或不适合上传到第三方服务的内容。

Rule-based mode works without an API key. LLM enhancement is optional and can improve summaries, topic extraction, mock exams, flashcards, and sprint plans.

## 导出格式 / Export Formats

| 格式 | 文件类型 | 使用场景 |
|---|---|---|
| Markdown | `.md` | 适合继续编辑、发布到笔记软件或版本管理。 |
| Word | `.docx` | 适合打印、交作业式整理或二次排版。 |
| PDF | `.pdf` | 适合固定格式分享和归档。 |
| Anki | `.csv` | 适合导入 Anki，字段为 `Front, Back, Tags`。 |

## 项目结构 / Project Structure

```text
.
├─ backend/                 # FastAPI 后端
│  ├─ app/                  # API、解析、OCR、生成、导出服务
│  ├─ tests/                # 后端测试
│  ├─ uploads/              # 本地上传目录，仅保留 .gitkeep
│  └─ outputs/              # 本地导出目录，仅保留 .gitkeep
├─ frontend/                # React + TypeScript 前端
│  └─ src/                  # 页面、组件、样式和测试
├─ examples/                # 虚构示例材料
├─ scripts/                 # 启动、测试、清理、打包脚本
├─ installer/               # Inno Setup 安装包配置
├─ docs/                    # 项目文档
├─ desktop_main.py          # Windows exe 启动入口
└─ ExamReviewAgent.spec     # PyInstaller 打包配置
```

## 开发者运行方式 / Development

安装并运行后端测试：

```powershell
cd backend
python -m pytest
```

安装并运行前端测试：

```powershell
cd frontend
npm install
npm run test -- --run
```

前端构建：

```powershell
cd frontend
npm run build
```

一键测试后端、前端和前端构建：

```powershell
.\scripts\test-all.ps1
```

清理本地上传、导出和缓存：

```powershell
.\scripts\reset-local-data.ps1
```

## Windows exe 使用说明 / Windows App

发布 GitHub Release 后，普通用户可以从 Release 页面下载以下文件：

- `ExamForgeAISetup-0.3.0.exe`：推荐普通用户下载，安装后从开始菜单启动。
- `ExamForgeAI.exe`：便携版，可直接运行测试。

安装后启动：

```text
ExamForge AI 期末复习资料生成器
```

运行数据保存在用户目录，不污染安装目录：

```text
%LOCALAPPDATA%\ExamForgeAI
```

包含：

- `uploads`：本地上传文件。
- `outputs`：导出的复习资料。
- `logs`：启动和运行日志。

## 打包 exe 方式 / Packaging

本地打包 Windows exe：

```powershell
.\scripts\build-windows.ps1
```

跳过测试打包：

```powershell
.\scripts\build-windows.ps1 -SkipTests
```

跳过安装包生成：

```powershell
.\scripts\build-windows.ps1 -SkipInstaller
```

成功后输出：

```text
dist\ExamForgeAI.exe
dist\installer\ExamForgeAISetup-0.3.0.exe
```

打包说明见：

```text
docs/windows-packaging.md
```

## GitHub Release

推送形如 `v0.3.0` 的 tag 后，GitHub Actions 会尝试在 Windows 环境中构建 exe 并创建 Release：

```powershell
git tag v0.3.0
git push origin v0.3.0
```

如果项目仓库尚未开启 Actions 或 Release 权限，请先检查 `.github/workflows/windows-release.yml` 的权限配置。

## Roadmap

以下方向会继续迭代，具体实现以 Release 版本为准：

- 更稳定的扫描件版面分析和题目切分。
- 更细粒度的章节映射和课程大纲识别。
- 更多本地模型和国产大模型 Provider。
- 更完整的桌面端体验，例如托盘图标、自动更新和离线模型管理。
- 更丰富的导出模板和打印样式。
- CI 状态、覆盖率和 Star History 图表接入真实仓库数据。

## 常见问题 / FAQ

### 没有 API Key 能用吗？

可以。本地整理模式无需 API Key，可以生成基础复习资料。大模型增强是可选功能。

### 扫描试卷一定能识别吗？

OCR 效果取决于图片清晰度、语言数据、版面复杂度和所选 Provider。文字版 PDF、PPTX、DOCX、Markdown 通常更稳定。

### 这个项目会承诺提分或押题吗？

不会。ExamForge AI 的目标是帮助整理复习材料和生成练习内容，不承诺考试结果，也不提供“必中押题”类表述。

### 上传文件会传到云端吗？

默认本地整理模式和本地解析在本机运行。如果你主动配置云 OCR 或大模型服务，相关文本或图片可能会发送给对应 Provider，请自行确认服务条款和隐私要求。

### Windows 首次启动很慢怎么办？

首次启动可能需要初始化依赖、OCR 组件或本地服务。可以运行诊断脚本查看环境状态：

```powershell
.\scripts\doctor.ps1
```

## 贡献 / Contributing

欢迎提交 Issue、建议和 Pull Request。建议在提交前运行：

```powershell
.\scripts\test-all.ps1
```

如果你的改动涉及 Windows 打包，请同时运行：

```powershell
.\scripts\build-windows.ps1
```

提交内容请避免包含：

- API Key、token、secret。
- 真实课程材料、真实试卷或版权受限文件。
- 个人隐私文件、本地路径和日志。
- `node_modules/`、`.venv/`、`dist/`、`build/` 等构建产物。

## 作者信息 / Author

作者：SiriZhao  
GitHub：[https://github.com/SiriZhao](https://github.com/SiriZhao)

ExamForge AI 保留英文项目名，中文名为“期末复习资料生成器”。项目主要面向中文大学生用户，同时保留英文介绍，方便国际用户理解和搜索。

## License

本项目采用 MIT License，详见 [LICENSE](LICENSE)。

