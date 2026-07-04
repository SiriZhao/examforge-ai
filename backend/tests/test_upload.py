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
            ("files", ("lecture.pdf", b"pdf content", "application/pdf")),
            ("files", ("diagram.png", b"image content", "image/png")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Uploaded 2 file(s)."
    assert len(body["files"]) == 2
    assert body["files"][0]["original_filename"] == "lecture.pdf"
    assert body["files"][0]["file_type"] == ".pdf"
    assert body["files"][0]["file_size"] == len(b"pdf content")
    assert (tmp_path / body["files"][0]["saved_filename"]).exists()
    assert body["files"][1]["original_filename"] == "diagram.png"
    assert body["files"][1]["file_type"] == ".png"
    assert (tmp_path / body["files"][1]["saved_filename"]).exists()


def test_upload_accepts_txt_file(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    client = TestClient(app)

    response = client.post("/upload", files=[("files", ("notes.txt", b"notes", "text/plain"))])

    assert response.status_code == 200
    assert response.json()["files"][0]["file_type"] == ".txt"


def test_upload_rejects_unsupported_file_type(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=[("files", ("script.exe", b"binary", "application/octet-stream"))],
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_rejects_empty_file(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    client = TestClient(app)

    response = client.post("/upload", files=[("files", ("empty.pdf", b"", "application/pdf"))])

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_file_count_limit(tmp_path: Path) -> None:
    settings.upload_dir = tmp_path
    original_limit = settings.max_files_per_request
    settings.max_files_per_request = 1
    client = TestClient(app)
    try:
        response = client.post(
            "/upload",
            files=[
                ("files", ("a.pdf", b"a", "application/pdf")),
                ("files", ("b.pdf", b"b", "application/pdf")),
            ],
        )
    finally:
        settings.max_files_per_request = original_limit

    assert response.status_code == 413
