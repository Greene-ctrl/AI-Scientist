from gradio_client import Client
import os
from typing import List, Dict, Any

import requests
import uuid

class WebResearcher:
    def __init__(self):
        self.web_search_space = "victor/websearch"
        self.hf_search_space = "John6666/testwarm"
        self.github_mcp_url = "https://harvesthealth-github-mcp-server.hf.space/"
        self._web_client = None
        self._hf_client = None

    @property
    def web_client(self):
        if self._web_client is None:
            try:
                self._web_client = Client(self.web_search_space)
            except Exception as e:
                print(f"Failed to connect to Gradio Client {self.web_search_space}: {e}")
        return self._web_client

    @property
    def hf_client(self):
        if self._hf_client is None:
            try:
                self._hf_client = Client(self.hf_search_space)
            except Exception as e:
                print(f"Failed to connect to Gradio Client {self.hf_search_space}: {e}")
        return self._hf_client

    def search_web(self, query: str, search_type: str = "search", num_results: int = 4) -> str:
        if self.web_client is None:
            return "Web search unavailable."
        try:
            return self.web_client.predict(
                query=query,
                search_type=search_type,
                num_results=num_results,
                api_name="/search_web"
            )
        except Exception as e:
            return f"Web search failed: {e}"

    def search_hf(self, query: str, repo_types: List[str] = ["model", "space"], limit: int = 5) -> str:
        if self.hf_client is None:
            return "HF search unavailable."
        try:
            result = self.hf_client.predict(
                repo_types=repo_types,
                sort="trending_score",
                sort_method="descending order",
                filter_str="",
                search_str=query,
                author="",
                tags="",
                infer="all",
                gated="all",
                appr=["auto", "manual"],
                size_categories=[],
                limit=limit,
                hardware=[],
                stage=[],
                fetch_detail=["Space Runtime"],
                show_labels=["Type", "ID", "Likes", "DLs"],
                api_name="/search"
            )
            # result[0] is a Dict with headers and data
            if isinstance(result, tuple) and len(result) > 0:
                data = result[0].get("data", [])
                return f"Found HF components: {data}"
            return str(result)
        except Exception as e:
            return f"HF search failed: {e}"

    def research_github(self, topic: str) -> str:
        # Try specialized GitHub MCP search first
        try:
            mcp_result = self.search_github_mcp(topic)
            if "failed" not in mcp_result.lower() and "unavailable" not in mcp_result.lower():
                return mcp_result
        except Exception as e:
            print(f"GitHub MCP search failed, falling back to web search: {e}")

        # Fallback to web search
        query = f"site:github.com {topic} repository"
        return self.search_web(query)

    def search_github_mcp(self, query: str) -> str:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": "search_repositories",
                "arguments": {
                    "query": query
                }
            }
        }
        try:
            response = requests.post(self.github_mcp_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            if "result" in result:
                return str(result["result"])
            return str(result)
        except Exception as e:
            return f"GitHub MCP search failed: {e}"

    def research_hf_spaces(self, topic: str) -> str:
        # Use deep HF search for better results
        return self.search_hf(topic, repo_types=["space"])
