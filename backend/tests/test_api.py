import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data


def test_analyze_valid_code():
    payload = {
        "title": "Pair Finder",
        "code": """def find_pairs(arr):
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            print(arr[i], arr[j])
    return True
"""
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["time_complexity"] == "O(n²)"
    assert data["confidence"] == "HIGH"
    assert "Two nested loops" in data["complexity_reasoning"]
    assert len(data["structure"]["nodes"]) > 0
    assert len(data["graph"]["growth_points"]) > 0


def test_analyze_syntax_error():
    payload = {
        "title": "Syntax Bug",
        "code": "def foo(\n   print('missing parenthesis'"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] is not None
    assert data["error"]["line"] >= 1


def test_analyze_empty_code():
    payload = {
        "title": "Empty Code",
        "code": "   "
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400


def test_history_endpoint():
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
