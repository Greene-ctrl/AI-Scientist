import json
from typing import List, Dict, Any
from openai import OpenAI
import os

class BaseAgent:
    def __init__(self, model: str = "gpt-4o", openai_api_key: str = None):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def _get_response(self, system_prompt: str, user_prompt: str, response_format=None) -> Any:
        # For testing purposes without API key or with dummy key
        api_key = self.client.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "dummy":
            return self._mock_response(system_prompt)

        args = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        if response_format:
            args["response_format"] = response_format

        response = self.client.chat.completions.create(**args)
        content = response.choices[0].message.content

        if response_format and response_format.get("type") == "json_object":
            return json.loads(content)
        return content

    def _mock_response(self, system_prompt: str) -> Any:
        if "planner" in system_prompt.lower():
            return {
                "steps": [
                    {"index": 0, "sub_question": "Analyze project structure", "tool_type": "doc_search"},
                    {"index": 1, "sub_question": "Identify core logic flaws", "tool_type": "doc_search"}
                ],
                "reasoning": "Standard analysis flow"
            }
        elif "weakness" in system_prompt.lower():
            return {
                "summary": "The code has several architectural issues.",
                "weaknesses": ["Manual memory management in Python", "Lack of unit tests"],
                "severity": "high"
            }
        return "Mocked response"

class Planner(BaseAgent):
    def plan(self, project_overview: str, has_code: bool = True) -> Dict[str, Any]:
        if has_code:
            system_prompt = """You are an expert query planner for a deep-thinking codebase analysis system.
Your task is to decompose complex codebase investigations into sequential execution plans.
Guidelines:
- Create 2-5 steps that build on each other.
- Each step should have a clear sub-question targeting a specific architectural or logic component.
- Specify tool_type: doc_search (for code retrieval)."""
        else:
            system_prompt = """You are an expert architect planning the design of a new modular software system.
Your task is to decompose the project description into sequential design steps.
Guidelines:
- Create 2-5 steps focusing on component decomposition and external service discovery.
- Each step should target a specific functional module or API integration.
- Specify tool_type: doc_search (for documentation or concept search)."""
        user_prompt = f"Decompose the following project overview into a sequential execution plan:\n\nProject Overview: {project_overview}\n\nRespond with valid JSON in this EXACT format:\n{{\n  'steps': [\n    {{\n      'index': 0,\n      'sub_question': 'What specific architectural component needs analysis?',\n      'tool_type': 'doc_search',\n      'expected_outputs': ['finding 1', 'finding 2']\n    }}\n  ],\n  'reasoning': 'Explain why this plan will effectively find weaknesses.'\n}}"
        return self._get_response(system_prompt, user_prompt, response_format={"type": "json_object"})

class WeaknessAnalyzer(BaseAgent):
    def analyze(self, context: str) -> Dict[str, Any]:
        system_prompt = """You are an AI senior engineer and architect reviewing a project or requirements for critical weaknesses.
Be critical and cautious. Focus on:
- Architectural flaws (circular dependencies, lack of modularity, tight coupling).
- Missing high-value external integrations.
- Potential performance bottlenecks.
- Redundant custom logic that could be replaced by standard libraries or models."""
        user_prompt = f"Analyze the following context (code or requirements) for weaknesses or missing components:\n\n{context}\n\nRespond in JSON format with fields: 'summary', 'weaknesses' (list of strings), 'severity' (high/medium/low)."
        return self._get_response(system_prompt, user_prompt, response_format={"type": "json_object"})

class AgentOrchestrator:
    def __init__(self, indexer: Any, openai_api_key: str = None):
        self.indexer = indexer
        self.planner = Planner(openai_api_key=openai_api_key)
        self.analyzer = WeaknessAnalyzer(openai_api_key=openai_api_key)

    def run_analysis(self, project_overview: str, has_code: bool = True) -> Dict[str, Any]:
        # 1. Plan
        plan = self.planner.plan(project_overview, has_code=has_code)

        all_weaknesses = []
        # 2. Execute steps
        for step in plan.get("steps", []):
            sub_q = step.get("sub_question")
            # Search codebase
            results = self.indexer.search(sub_q, limit=3)
            if results:
                context = "\n---\n".join([r.get("text", "") for r in results])
            else:
                # If no code results, use the sub-question itself as context for conceptual analysis
                context = f"No code snippets found for: {sub_q}. Analyzing based on project overview: {project_overview}"

            # Analyze
            analysis = self.analyzer.analyze(context)
            all_weaknesses.extend(analysis.get("weaknesses", []))

        return {
            "plan": plan,
            "weaknesses": list(set(all_weaknesses)),
            "status": "completed"
        }
