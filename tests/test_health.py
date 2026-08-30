from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health_connected(monkeypatch):
    monkeypatch.setattr("app.api.routes.check_database_connection", lambda: True)
    r=client.get("/health"); assert r.status_code==200; assert r.json()["database"]=="connected"

def test_health_degraded(monkeypatch):
    monkeypatch.setattr("app.api.routes.check_database_connection", lambda: False)
    r=client.get("/health"); assert r.status_code==503; assert r.json()["status"]=="degraded"
