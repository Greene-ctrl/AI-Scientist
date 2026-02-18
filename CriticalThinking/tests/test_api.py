from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_analyze_flow():
    # Submit analysis
    response = client.post("/analyze", json={"repo_url": "local://.", "project_description": "Test Project"})
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    assert task_id

    # Wait a bit for background task
    time.sleep(1)

    response = client.get(f"/report/{task_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"Task status: {data['status']}")
    if data['status'] == 'failed':
        print(f"Error: {data.get('error')}")

    assert data["status"] != "failed"
