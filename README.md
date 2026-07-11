# Campus AI Workspace

> Campus AI Workspace is the next evolution of ExamForge AI.

你的个人 AI 学习与开发工作台：无需注册，用户自带模型，数据默认保存在本地。原有 OCR、多文件证据整理、长文档分块、复习资料、模拟题、Anki 与多格式导出能力继续作为 **ExamForge Review Engine** 提供。

当前版本：**v0.5.1**
仓库：[SiriZhao/examforge-ai](https://github.com/SiriZhao/examforge-ai)
许可：MIT

## 核心能力

- 无注册、无登录、无 JWT 的本地工作空间。
- SQLite `workspace.db` 保存课程、聊天、知识块、记忆与 Agent 任务。
- PDF、PPTX、DOCX、Markdown、TXT 和图片解析；扫描内容支持 OCR。
- 课程知识库、分块检索与真实 `chunk_id`、文件名、页码引用。
- 学习 Agent 任务规划与显式记忆管理。
- ExamForge 复习资料、往年题分析、模拟卷、Anki CSV、Markdown/DOCX/PDF 导出。
- DeepSeek、OpenAI、OpenAI Compatible、Claude Compatible 的浏览器本地 BYOK 配置。
- Docker Web 版和 Windows 桌面版。

## 使用方法

1. 打开应用，首次点击“开始使用”。
2. 在“设置”中选择供应商，填写 API Key、Base URL 和模型名称。
3. 配置只保存在当前浏览器；测试连接由浏览器直连供应商，不经过项目后端。
4. 创建课程，上传课件、教材、笔记或往年题。
5. 使用课程知识库、Agent 任务或进入“复习资料”生成完整资料包。

未配置模型时不会报错，系统会提示前往设置；课程知识库、OCR 和 ExamForge 本地安全底稿仍可使用。部分模型供应商不允许浏览器跨域请求，此时浏览器直连测试可能失败，Key 仍不会上传到 Campus AI Workspace 服务器。

## 数据控制

- “设置 → 导出工作空间”导出课程、对话和记忆元数据，不包含 API Key。
- “设置 → 清空本地数据”删除 SQLite 业务数据和工作空间上传文件。
- API Key 位于浏览器 `localStorage`，清理浏览器站点数据即可移除。
- 当前“导入工作空间”仍在格式校验设计阶段，界面不会伪装为已完成。

## 本地开发

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

另开终端：

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL="http://127.0.0.1:8000/api"
npm run dev
```

访问 `http://localhost:5173`。

## Docker

```bash
docker compose up --build
```

访问 `http://127.0.0.1:8000`、`/api/health` 和 `/api/ready`。容器使用持久化 volume 保存 `/data/workspace.db` 和课程资料。

云端版本仍是单一私人工作空间，不具备多用户隔离。不要把无访问控制的实例直接公开给不受信任用户；建议放在 VPN、反向代理认证或平台访问控制之后，并启用 HTTPS 和严格 CORS。

## Windows 桌面版

```powershell
.\scripts\build-windows.ps1
```

输出：

- `dist/CampusAIWorkspace.exe`
- `dist/installer/CampusAIWorkspaceSetup-0.5.1.exe`（本机有 Inno Setup 时）

构建产物只上传 GitHub Release，不提交到 `main`。

## API 与隐私

- 新工作台 API 前缀为 `/api/v1`，无需认证，仅用于单一私人工作空间。
- 后端没有保存 BYOK Key 的接口，不记录 Authorization 或完整用户材料。
- 旧 ExamForge Review Engine 仍保留兼容 Provider；使用前应确认供应商隐私条款。
- 不要上传无权处理的课程、考试或个人敏感资料。

## 当前边界

课程检索目前是带真实引用的关键词检索 MVP；向量检索、SSE 流式聊天、项目代码 Diff、受限工具执行和工作空间导入仍在 Roadmap。Python 工具默认关闭。生成内容仅供学习辅助，用户应核对原始材料和教师要求。

## 文档

- [架构](docs/architecture.md)
- [API](docs/api.md)
- [数据库](docs/database.md)
- [开发](docs/development.md)
- [安全](docs/security.md)
- [隐私](docs/privacy.md)
- [云端部署](docs/cloud-deployment.md)
- [Windows 桌面版](docs/windows-desktop.md)

## License

[MIT License](LICENSE) © SiriZhao
