# Campus AI Workspace v0.5.1

## 本地工作空间重构

- 移除不完整的注册、登录、密码、JWT、用户表与 SaaS 账号依赖。
- 启动后直接进入 Chat Workspace，首次显示本地隐私欢迎引导。
- 课程、对话、知识块、记忆和 Agent 任务保存到本地 `workspace.db`。
- 未配置模型时显示可操作提示，不再触发认证 404。

## BYOK

- 设置页支持 DeepSeek、OpenAI、OpenAI Compatible 和 Claude Compatible。
- API Key、Base URL 和模型名称只保存在当前浏览器。
- 测试连接由浏览器直连供应商，不经过 Campus AI Workspace 后端。
- 增加网络错误、Key 错误、接口不存在和超时提示。

## 数据与核心功能

- 增加导出工作空间和清空本地数据。
- 保留课程文件解析、OCR、知识库检索、真实引用和 Agent 任务。
- 完整保留 ExamForge Review Engine 的复习资料、模拟卷、Anki 和多格式导出。

## 发布产物

- `CampusAIWorkspace.exe`
- `CampusAIWorkspaceSetup-0.5.1.exe`

当前云端模式仍是单一私人工作空间，不应在无访问控制时公开给不受信任用户。
