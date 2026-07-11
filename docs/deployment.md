# 部署模式

| 模式 | 用途 |
| --- | --- |
| `local_dev` | Vite 与 FastAPI 本地开发 |
| `desktop` | PyInstaller 打包的私密 Windows 桌面版 |
| `cloud` | Docker 托管的网页端 |

云端部署见 [cloud-deployment.md](cloud-deployment.md)，桌面打包见 [windows-packaging.md](windows-packaging.md)。公共云端默认使用临时匿名工作空间，不配置开发者统一模型 Key。
