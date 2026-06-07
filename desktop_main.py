import logging
import multiprocessing
import os
import socket
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

import uvicorn
from fastapi.staticfiles import StaticFiles


APP_NAME = "ExamForgeAI"
DISPLAY_NAME = "ExamForge AI"


def resource_path(*parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base.joinpath(*parts)


def user_data_dir() -> Path:
    root = os.getenv("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    path = Path(root) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_runtime_dirs() -> tuple[Path, Path, Path]:
    data_dir = user_data_dir()
    uploads = data_dir / "uploads"
    outputs = data_dir / "outputs"
    logs = data_dir / "logs"
    uploads.mkdir(parents=True, exist_ok=True)
    outputs.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    os.environ["ERA_UPLOAD_DIR"] = str(uploads)
    os.environ["ERA_OUTPUT_DIR"] = str(outputs)
    os.environ["ERA_APP_NAME"] = DISPLAY_NAME
    return uploads, outputs, logs


def configure_logging(logs_dir: Path) -> Path:
    log_path = logs_dir / "desktop.log"
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        encoding="utf-8",
    )
    return log_path


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def mount_frontend(app) -> None:
    frontend_dist = resource_path("frontend_dist")
    index_file = frontend_dist / "index.html"
    if not index_file.exists():
        raise RuntimeError(f"Frontend assets were not found: {frontend_dist}")
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


def open_browser_later(url: str) -> None:
    time.sleep(1.2)
    webbrowser.open(url)


def show_failure_message(message: str, log_path: Path) -> None:
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            0,
            f"{message}\n\n日志文件：{log_path}",
            DISPLAY_NAME,
            0x10,
        )
    except Exception:
        pass


def main() -> None:
    multiprocessing.freeze_support()
    _, _, logs_dir = configure_runtime_dirs()
    log_path = configure_logging(logs_dir)
    logger = logging.getLogger("desktop")

    try:
        logger.info("Starting %s", DISPLAY_NAME)
        logger.info("User data directory: %s", user_data_dir())

        from app.main import app

        mount_frontend(app)
        port = find_free_port()
        url = f"http://127.0.0.1:{port}"
        logger.info("Serving local app at %s", url)

        threading.Thread(target=open_browser_later, args=(url,), daemon=True).start()
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            log_config=None,
            access_log=False,
        )
    except Exception as exc:
        logger.error("Desktop startup failed: %s", exc)
        logger.error(traceback.format_exc())
        show_failure_message(
            "ExamForge AI 启动失败。请查看日志文件，或重新安装后再试。",
            log_path,
        )
        raise


if __name__ == "__main__":
    main()
