# 数据库

默认 `DATABASE_URL=sqlite:///./workspace.db`。表包括工作空间课程、对话、消息、课程文件、知识块、记忆和 Agent 任务，不包含用户表。

应用启动时使用 SQLAlchemy `create_all` 创建缺失表。v0.5.1 不再维护 SaaS 账号迁移；旧测试或开发数据库可以删除后由应用重建。导出工作空间不会包含浏览器中的 API Key。
