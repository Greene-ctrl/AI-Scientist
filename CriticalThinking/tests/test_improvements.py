from app.services.hf_matcher import HFMatcher
from app.services.improvement_agent import ImprovementAgent
from unittest.mock import MagicMock

def test_hf_matcher():
    matcher = HFMatcher()
    # Mocking HFApi.list_models
    matcher.api.list_models = MagicMock()
    mock_model = MagicMock()
    mock_model.id = "test/model"
    mock_model.downloads = 100
    mock_model.likes = 10
    matcher.api.list_models.return_value = [mock_model]

    results = matcher.find_replacements("sentiment analysis")
    assert len(results) == 1
    assert results[0]["id"] == "test/model"

def test_improvement_agent():
    agent = ImprovementAgent(openai_api_key="dummy")
    result = agent.generate_improvements(["Weakness 1"])
    assert "improvements" in result
    assert len(result["improvements"]) > 0
    assert "replacement_search_query" in result["improvements"][0]
