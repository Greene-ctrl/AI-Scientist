# CriticalThinking Project Structure

## 1. Project Description
**CriticalThinking** is an autonomous agent system that performs deep architectural analysis of software projects. Inspired by `deep-thinking-agent` and `AI-Scientist`, it moves beyond simple linting to identify high-level design weaknesses, suggest structural improvements, and recommend state-of-the-art replacements (e.g., Hugging Face models) for custom implementations.

### In-app Integrations
- **Git-based Indexer**: Automatically clones and indexes codebases.
- **Deep-Thinking Orchestrator**: Uses iterative planning and reasoning (Planner -> Retriever -> Analyzer).
- **Hypothesis Generator**: Generates "Improvement Hypotheses" and validates them against the code context.
- **Hugging Face Hub**: Searches for replacement components.
- **Web Researcher**: Uses specialized MCP servers (harvesthealth/github-mcp-server) and Gradio clients to search GitHub and Hugging Face Spaces for community-driven solutions.

### Proposed FASTAPI Setup
- **App structure**:
  - `main.py`: App entry point.
  - `api/router.py`: API routes.
  - `services/`: Business logic and agent orchestration.
  - `tests/`: Automated tests.
- **Dependency injection**: Services are initialized per-task with appropriate configuration (LLM model, API keys).

## 2. Tasks and Tests
### Backend & Infrastructure
- **Task: Project Scaffolding**
  - *Test*: `tests/test_main.py` -> Verifies health check.
- **Task: Codebase Indexing Service**
  - *Test*: `tests/test_indexer.py` -> Verifies cloning, chunking, and search.

### Agent Logic
- **Task: Multi-Agent Orchestration**
  - *Test*: `tests/test_orchestrator.py` -> Verifies planning and analysis loop.
- **Task: Improvement & Replacement Logic**
  - *Test*: `tests/test_improvements.py` -> Verifies roadmap generation and HF matching.

### API & End-to-End
- **Task: API Exposure & Background Jobs**
  - *Test*: `tests/test_api.py` -> Verifies the full /analyze -> /report flow.

## 3. Functionality Expectations
### User Perspective
- Submit a repository URL.
- Receive a "Critical Thinking Report".
- View "Critical Weaknesses" and an "Improvement Roadmap".
- See "Suggested Replacements" (libraries/models) for custom code.

### Technical Perspective
- **Iterative Reasoning**: The agent doesn't just look at code once; it plans its investigation and refines its findings.
- **Schema-Aware RAG**: Uses structural context to find relevant code snippets.
- **External Knowledge**: Connects to Hugging Face Hub for modernization suggestions.

## 4. API Endpoints
- **POST /analyze**
  - Request: `{"repo_url": "string", "project_description": "string"}`
  - Response: `{"task_id": "uuid"}`
- **GET /report/{task_id}**
  - Response: `{"status": "completed", "report": {"weaknesses": [], "improvements": []}}`
