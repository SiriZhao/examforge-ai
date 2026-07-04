from fastapi.testclient import TestClient

from app.main import app


def test_error_response_has_unified_shape() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=[("files", ("notes.exe", b"notes", "application/octet-stream"))],
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] is True
    assert body["message"] == "Unsupported file type: .exe."
    assert body["detail"] == "Unsupported file type: .exe."
