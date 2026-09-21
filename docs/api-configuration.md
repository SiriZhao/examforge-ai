# API 配置

RecallForge AI 使用用户自己的模型 API。配置保存在浏览器本地，不写入报告数据库或日志。填写 Provider、Base URL、模型名称和 API Key 后可测试连接；认证失败、模型不存在、超时、限流和网络错误都会显示中文说明。

公共网页必须使用 HTTPS。服务商若不允许浏览器跨域请求，测试连接会失败，但 Key 不会通过 RecallForge 服务端转存。
