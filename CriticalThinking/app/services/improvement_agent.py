from typing import List, Dict, Any
from app.services.agent_orchestrator import BaseAgent

class ImprovementAgent(BaseAgent):
    def generate_improvements(self, weaknesses: List[str]) -> Dict[str, Any]:
        system_prompt = """You are an AI research scientist and senior architect with a focus on modular, API-driven design.
Your goal is to generate impactful ideas for improving a codebase or designing a new one by integrating high-value external components.
Key Principles:
- Decompose the project into independent, modular components that communicate via FastAPI endpoints.
- Identify state-of-the-art Hugging Face Models/Spaces or GitHub projects that can serve as functional building blocks.
- **Strict Critical Judgment**: Only suggest an external project if it is exceptionally useful and provides significant advantages over a custom implementation.
- Focus on reducing custom code and maintenance by leveraging established open-source ecosystems."""
        user_prompt = f"Given these weaknesses or project requirements:\n{weaknesses}\n\nPropose a strategic improvement roadmap focusing on modularity and external integrations. Respond in JSON with format:\n{{\n  'improvements': [\n    {{\n      'component_or_weakness': 'the target component or identified weakness',\n      'proposal': 'detailed plan for integration or improvement',\n      'justification': 'critical reasoning for why this external project or approach is high-value',\n      'replacement_search_query': 'specific query for Hugging Face or GitHub discovery',\n      'utility_score': 1-10,\n      'feasibility': 1-10\n    }}\n  ]\n}}"
        return self._get_response(system_prompt, user_prompt, response_format={"type": "json_object"})

    def _mock_response(self, system_prompt: str) -> Any:
        return {
            "improvements": [
                {
                    "component_or_weakness": "Memory Management",
                    "proposal": "Integrate a specialized Rust-based memory optimizer via a Python wrapper.",
                    "justification": "Significant reduction in overhead for high-throughput data processing.",
                    "replacement_search_query": "python rust memory management",
                    "utility_score": 8,
                    "feasibility": 7
                },
                {
                    "component_or_weakness": "Sentiment Analysis",
                    "proposal": "Replace custom rule-based system with a hosted Hugging Face Space API.",
                    "justification": "LLM-based models provide far superior accuracy for nuanced text.",
                    "replacement_search_query": "sentiment analysis space",
                    "utility_score": 9,
                    "feasibility": 10
                }
            ]
        }
