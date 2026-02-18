from fastapi.testclient import TestClient
from app.main import app
import time
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("app.api.router.CodeIndexer")
@patch("app.api.router.WebResearcher")
def test_analyze_flow(mock_web_researcher_class, mock_indexer_class):
    # Mock CodeIndexer
    mock_indexer = MagicMock()
    mock_indexer_class.return_value = mock_indexer

    # Mock WebResearcher
    mock_web_researcher = MagicMock()
    mock_web_researcher_class.return_value = mock_web_researcher
    mock_web_researcher.research_github.return_value = "Mocked GitHub results"
    mock_web_researcher.research_hf_spaces.return_value = "Mocked HF Spaces results"

    # Submit analysis
    response = client.post("/analyze", json={"repo_url": "https://github.com/dummy/repo", "project_description": "Test Project"})
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

    assert data["status"] == "completed"
    assert "github_research" in data["report"]["improvements"][0]
    assert "hf_spaces_research" in data["report"]["improvements"][0]
