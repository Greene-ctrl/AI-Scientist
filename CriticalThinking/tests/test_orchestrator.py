import pytest
from app.services.agent_orchestrator import AgentOrchestrator
from unittest.mock import MagicMock

def test_orchestrator_flow():
    mock_indexer = MagicMock()
    mock_indexer.search.return_value = [{"text": "print('hello')"}]

    orchestrator = AgentOrchestrator(indexer=mock_indexer, openai_api_key="dummy")

    # Run analysis (will use mock responses from BaseAgent._mock_response)
    result = orchestrator.run_analysis("A simple python script")

    assert "plan" in result
    assert "weaknesses" in result
    assert result["status"] == "completed"
    assert len(result["weaknesses"]) > 0
    assert mock_indexer.search.called
