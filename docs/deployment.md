# Deployment

ExamForge AI supports three modes:

| Mode | How it runs | Best for |
| --- | --- | --- |
| `local_dev` | Vite dev server + FastAPI dev server | Development |
| `desktop` | Windows exe built by PyInstaller/Inno Setup | Private local use |
| `cloud` | Docker container serving FastAPI + frontend SPA | Browser-only web app |

For cloud deployment, see [cloud-deployment.md](cloud-deployment.md).

For Windows desktop packaging, see [windows-packaging.md](windows-packaging.md).
