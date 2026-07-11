# 架构

v0.5.1 采用本地优先、单一工作空间架构。React/Vite 前端直接进入 Chat Workspace；FastAPI 提供文件解析、OCR、知识库、Agent 和 ExamForge Review Engine。数据通过 SQLAlchemy 2 写入 SQLite `workspace.db`。

模型配置只保存在浏览器。设置页的连接测试由浏览器直接请求供应商，不经过本项目后端。当前不包含注册、密码、JWT、用户表或多用户隔离。

知识库流程：安全上传 → 解析/OCR → 语义分块 → 内容哈希 → 课程过滤检索 → 真实引用。向量检索和重排序属于 Roadmap。
