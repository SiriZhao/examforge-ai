from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def test_upload_multiple_files(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=[
            (
                "files",
                ("lecture.pdf", b"pdf content", "application/pdf"),
            ),
            (
                "files",
                (
                    "diagram.png",
                    b"image content",
                    "image/png",
                ),
            ),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "已成功上传 2 个文件。"
    assert len(body["files"]) == 2
    assert body["files"][0]["original_filename"] == "lecture.pdf"
    assert body["files"][0]["file_type"] == ".pdf"
    assert body["files"][0]["file_size"] == len(b"pdf content")
    assert (tmp_path / body["files"][0]["saved_filename"]).exists()
    assert body["files"][1]["original_filename"] == "diagram.png"
    assert body["files"][1]["file_type"] == ".png"
    assert (tmp_path / body["files"][1]["saved_filename"]).exists()


def test_upload_rejects_unsupported_file_type(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=[("files", ("notes.txt", b"notes", "text/plain"))],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "不支持的文件类型：.txt。"


def test_upload_rejects_empty_file(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=[("files", ("empty.pdf", b"", "application/pdf"))],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "上传文件为空：empty.pdf。"
