from fastapi.testclient import TestClient
from resume_analyzer.api.main import create_app

def test_health():
    client = TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
