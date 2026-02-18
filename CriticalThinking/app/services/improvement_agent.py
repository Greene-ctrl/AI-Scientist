from typing import List, Dict, Any
from app.services.agent_orchestrator import BaseAgent

class ImprovementAgent(BaseAgent):
    def generate_improvements(self, weaknesses: List[str]) -> Dict[str, Any]:
        system_prompt = """You are an AI research scientist and senior architect.
Your goal is to generate impactful and creative ideas for improving a codebase.
Consider:
- Refactoring for better scalability.
- Replacing custom implementations with state-of-the-art Hugging Face models or open-source projects.
- Improving performance and maintainability."""
        user_prompt = f"Given these weaknesses:\n{weaknesses}\n\nPropose a next-step improvement roadmap. Respond in JSON with format:\n{{\n  'improvements': [\n    {{\n      'weakness': 'the identified weakness',\n      'proposal': 'detailed improvement plan',\n      'replacement_search_query': 'query for Hugging Face or GitHub',\n      'interestingness': 1-10,\n      'feasibility': 1-10\n    }}\n  ]\n}}"
        return self._get_response(system_prompt, user_prompt, response_format={"type": "json_object"})

    def _mock_response(self, system_prompt: str) -> Any:
        return {
            "improvements": [
                {
                    "weakness": "Manual memory management",
                    "proposal": "Use a managed library",
                    "replacement_search_query": "memory management library"
                },
                {
                    "weakness": "Lack of sentiment analysis accuracy",
                    "proposal": "Use a pre-trained transformer model",
                    "replacement_search_query": "sentiment analysis"
                }
            ]
        }
