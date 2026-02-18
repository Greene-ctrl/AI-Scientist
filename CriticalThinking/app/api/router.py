from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import os
from app.services.indexer import CodeIndexer
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.improvement_agent import ImprovementAgent
from app.services.hf_matcher import HFMatcher
from app.services.web_researcher import WebResearcher

router = APIRouter()

# In-memory task store
tasks: Dict[str, Any] = {}

class AnalyzeRequest(BaseModel):
    repo_url: str
    project_description: Optional[str] = "Generic software project"

class AnalyzeResponse(BaseModel):
    task_id: str

async def run_analysis_task(task_id: str, repo_url: str, project_description: str):
    tasks[task_id]["status"] = "processing"
    try:
        api_key = os.getenv("OPENAI_API_KEY", "dummy")
        # Initialize services
        indexer = CodeIndexer(qdrant_url=":memory:", openai_api_key=api_key)
        orchestrator = AgentOrchestrator(indexer=indexer, openai_api_key=api_key)
        improver = ImprovementAgent(openai_api_key=api_key)
        matcher = HFMatcher()
        web_researcher = WebResearcher()

        # 1. Index
        indexer.index_repository(repo_url)

        # 2. Analyze
        analysis_results = orchestrator.run_analysis(project_description)
        weaknesses = analysis_results.get("weaknesses", [])

        # 3. Improvements
        improvements_results = improver.generate_improvements(weaknesses)
        improvements = improvements_results.get("improvements", [])

        # 4. Replacement matching and Web Research
        for imp in improvements:
            query = imp.get("replacement_search_query")
            if query:
                # Direct HF search
                replacements = matcher.find_replacements(query)
                imp["suggested_replacements"] = replacements

                # Web research for GitHub and HF Spaces
                imp["github_research"] = web_researcher.research_github(query)
                imp["hf_spaces_research"] = web_researcher.research_hf_spaces(query)

        # 5. Store report
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["report"] = {
            "project": project_description,
            "weaknesses": weaknesses,
            "improvements": improvements
        }
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "report": None}
    background_tasks.add_task(run_analysis_task, task_id, request.repo_url, request.project_description)
    return AnalyzeResponse(task_id=task_id)

@router.get("/report/{task_id}")
async def get_report(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]
