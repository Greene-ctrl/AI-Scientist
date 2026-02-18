import gradio as gr
from fastapi import FastAPI
from CriticalThinking.app.main import app as fastapi_app

# The FastAPI app is already initialized in CriticalThinking.app.main
# We can just mount it or use it as the main app.
# Here we will mount Gradio onto the existing FastAPI app.

import httpx

def analyze_interface(repo_url, project_description):
    if not repo_url and not project_description:
        return "Please provide at least a project description."

    try:
        # Call the local FastAPI endpoint
        with httpx.Client() as client:
            response = client.post(
                "http://localhost:7860/analyze",
                json={
                    "repo_url": repo_url if repo_url else None,
                    "project_description": project_description
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            task_id = data.get("task_id")
            return f"Analysis started! Task ID: {task_id}\n\nYou can check the report at: /report/{task_id}"
    except Exception as e:
        return f"Error starting analysis: {str(e)}"

def get_report_interface(task_id):
    if not task_id:
        return "Please provide a Task ID."
    try:
        with httpx.Client() as client:
            response = client.get(f"http://localhost:7860/report/{task_id}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return f"Error fetching report: {str(e)}"

with gr.Blocks(title="Critical Code Agent") as demo:
    gr.Markdown("# 🦀 Critical Code Agent")
    gr.Markdown("Autonomous agent system for deep architectural analysis and software weakness identification.")

    with gr.Row():
        repo_url = gr.Textbox(label="Repository URL (Optional)", placeholder="https://github.com/username/repo")
        project_desc = gr.Textbox(label="Project Description", placeholder="Brief description of the project")

    analyze_btn = gr.Button("Analyze Repository", variant="primary")
    output = gr.Textbox(label="Status")

    analyze_btn.click(analyze_interface, inputs=[repo_url, project_desc], outputs=output)

    gr.Markdown("### Check Report Status")
    with gr.Row():
        task_id_input = gr.Textbox(label="Task ID")
        report_btn = gr.Button("Get Report")

    report_output = gr.JSON(label="Analysis Report")
    report_btn.click(get_report_interface, inputs=[task_id_input], outputs=report_output)

    gr.Markdown("### API Endpoints")
    gr.Markdown("- `POST /analyze`: Submit a repository for analysis")
    gr.Markdown("- `GET /report/{task_id}`: Retrieve analysis report")
    gr.Markdown("- `GET /health`: Check service health")

# Mount Gradio to the FastAPI app
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
