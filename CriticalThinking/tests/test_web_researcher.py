import pytest
from app.services.web_researcher import WebResearcher
from unittest.mock import MagicMock, patch

@patch("requests.post")
def test_web_researcher_github_mcp(mock_post):
    researcher = WebResearcher()
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "MCP GitHub Result"}
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result = researcher.research_github("sentiment analysis")
    assert "MCP GitHub Result" in result
    mock_post.assert_called_once()

def test_web_researcher_github_fallback():
    researcher = WebResearcher()
    # Mock search_github_mcp to fail
    researcher.search_github_mcp = MagicMock(return_value="GitHub MCP search failed")

    with patch("app.services.web_researcher.Client") as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.predict.return_value = "Fallback Web Result"

        result = researcher.research_github("sentiment analysis")
        assert "Fallback Web Result" in result

def test_web_researcher_hf():
    researcher = WebResearcher()
    with patch("app.services.web_researcher.Client") as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.predict.return_value = ({"data": [["space", "example/space", 10, 100]]}, [])

        result = researcher.research_hf_spaces("sentiment analysis")
        assert "Found HF components" in result
        # Check that it tried to connect to John6666/testwarm
        mock_client_class.assert_any_call("John6666/testwarm")
