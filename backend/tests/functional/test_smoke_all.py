import pytest
from fastapi.testclient import TestClient
from src import app

@pytest.fixture
def client():
    return TestClient(app)

def test_smoke_all_routes(client):
    for route in app.routes:
        if hasattr(route, "methods"):
            method = list(route.methods)[0]
            path = route.path
            
            # replace path params with dummy values
            path = path.replace("{provider}", "google")
            path = path.replace("{project_id}", "00000000-0000-0000-0000-000000000000")
            path = path.replace("{user_id}", "00000000-0000-0000-0000-000000000000")
            path = path.replace("{token}", "dummy_token")
            
            if "{" in path:
                continue
                
            try:
                if method == "GET":
                    client.get(path)
                elif method == "POST":
                    client.post(path, json={})
                elif method == "PUT":
                    client.put(path, json={})
                elif method == "DELETE":
                    client.delete(path)
            except Exception:
                pass
