# API

- `GET /api/v1/workspace`
- `GET /api/v1/workspace/export`
- `DELETE /api/v1/workspace`
- `GET/POST/DELETE /api/v1/courses`
- `POST /api/v1/courses/{id}/files`
- `POST /api/v1/courses/{id}/search`
- `GET/POST /api/v1/conversations`
- `GET/POST /api/v1/conversations/{id}/messages`
- `GET/POST /api/v1/memory`
- `GET/POST /api/v1/agent/tasks`
- `GET /api/health`、`GET /api/ready`

这些接口属于单一私人工作空间，不使用登录或 JWT。不要把无访问控制的云端实例直接公开给不受信任用户。OpenAPI 以运行中的 `/docs` 为准。
