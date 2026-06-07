from fastapi.testclient import TestClient

from app.main import app


def test_error_response_has_unified_shape() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=[("files", ("notes.txt", b"notes", "text/plain"))],
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] is True
    assert body["message"] == "不支持的文件类型：.txt。"
    assert body["detail"] == "不支持的文件类型：.txt。"
