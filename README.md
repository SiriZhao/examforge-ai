# ExamForge AI

> AI Final Exam Review Pack Generator for University Students

ExamForge AI 是一个面向大学生期末考试的 AI 复习资料生成器。它不再试图成为通用工作台，而是专注把课件、教材、笔记、课程纲要、往年题和扫描试卷变成可复习、可刷题、可导出的资料系统。

当前版本：**v0.6.0**。项目曾尝试扩展为 Campus AI Workspace，现已重新聚焦于复习资料生成的深度、可靠性和可执行性。

## 为什么不是直接把 PDF 发给 ChatGPT

- 自动区分课程纲要、课件、教材、笔记、往年题、答案和错题的作用。
- 多文件证据整合：课程范围限制边界，往年题影响题型与重点，答案影响评分点。
- AI 深度整理走 LLM-first 分阶段流程：Document/Evidence → ChunkUnderstanding → CourseModel → StudyBlueprint → UnitDraft → 全局合成 → canonical Markdown；OCR、来源锚点、检查点和导出由 Python 基础设施负责。
- 生成重点优先级地图、复习讲义、往年题分析、题型攻略、模拟卷、主动回忆题、Anki 和冲刺计划。
- 可导出 Markdown、DOCX、PDF 与 Anki CSV。

## 五步流程

1. 创建复习项目：填写课程、考试日期、考试形式、每日时间、掌握程度和目标。
2. 上传并标记资料：PDF、PPTX、DOCX、Markdown、TXT、PNG、JPG、JPEG。
3. 查看资料诊断：完整度、资料角色、缺口、风险和推荐策略。
4. 分模块生成：重点地图、讲义、往年题分析、题型、模拟卷、Anki、易错点和冲刺计划。
5. 复习与导出：局部优化、保存版本、导出完整包或单独模块。

## BYOK

无需注册。用户自己提供 DeepSeek、OpenAI 或 OpenAI-compatible API 配置。

- API Key 默认只保存于当前浏览器 `localStorage`。
- 不写入工作空间数据库、日志、GitHub 或错误响应。
- 配置模型时默认使用 **AI 深度整理**；未配置模型时才使用 **基础离线整理**。离线报告只是兼容性应急路径，不是 AI 内容的知识基础。
- 公共网页使用时必须通过 HTTPS；部分服务商禁止浏览器跨域测试，界面会给出中文提示。

## 本地开发

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL="http://127.0.0.1:8000/api"
npm run dev
```

## Docker 和云端

```bash
docker build -t examforge-ai:0.6.0 .
docker run --rm -p 8000:8000 --env-file .env.example examforge-ai:0.6.0
```

云端模式为匿名工作空间：浏览器保存随机 `workspace_id` 与 secret，后端验证资源归属。上传文件和报告根据 `TEMP_FILE_TTL_HOURS` 定期清理；敏感资料建议使用桌面版。

Render：连接仓库，选择 Docker，Health Check 填 `/api/health`，挂载持久盘 `/data`。默认不设置开发者模型 Key，设置 `ENABLE_SERVER_LLM_KEY=false`。

Railway/Fly.io：使用根目录 Dockerfile，设置 `APP_MODE=cloud`、`APP_VERSION=0.6.0`、`PUBLIC_BASE_URL`、`CORS_ORIGINS` 和持久化 `/data`。

## Windows 桌面版

```powershell
.\scripts\build-windows.ps1
```

生成：

- `dist/ExamForgeAI.exe`
- `dist/installer/ExamForgeAISetup-0.6.0.exe`

桌面版通过 PyInstaller 打包前端静态资源，使用 `sys._MEIPASS` 查找 `frontend/dist`，双击后自动打开本地网页；文件、OCR 缓存和工作空间均保存在本机。

## 隐私与免责声明

- 不要上传无权处理的课程、考试或个人敏感资料。
- 外部模型生成内容仅作学习辅助，必须核对原始材料与教师要求。
- 不承诺押题准确，也不鼓励作弊或泄露考试内容。
- 公共云端应启用 HTTPS、上传限制、TTL 清理和访问隔离。

## Roadmap

- 模块级 LLM 生成与重试状态持久化。
- 更强的往年题分值分析、主动回忆题与在线自测。
- 单模块导出、报告编辑器和版本恢复界面。
- 向量检索与更精细的引用面板。

## License

[MIT License](LICENSE) © SiriZhao
