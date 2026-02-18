import gradio as gr
from fastapi import FastAPI
from CriticalThinking.app.main import app as fastapi_app

# The FastAPI app is already initialized in CriticalThinking.app.main
# We can just mount it or use it as the main app.
# Here we will mount Gradio onto the existing FastAPI app.

def analyze_interface(repo_url, project_description):
    # This is a placeholder for the Gradio UI to interact with the API
    # In a real scenario, we might want to use the background task or just call the service.
    return f"Analysis request for {repo_url} received. Please use the API endpoints to monitor progress."

with gr.Blocks(title="Critical Code Agent") as demo:
    gr.Markdown("# 🦀 Critical Code Agent")
    gr.Markdown("Autonomous agent system for deep architectural analysis and software weakness identification.")

    with gr.Row():
        repo_url = gr.Textbox(label="Repository URL (Optional)", placeholder="https://github.com/username/repo")
        project_desc = gr.Textbox(label="Project Description", placeholder="Brief description of the project")

    analyze_btn = gr.Button("Analyze Repository", variant="primary")
    output = gr.Textbox(label="Status")

    analyze_btn.click(analyze_interface, inputs=[repo_url, project_desc], outputs=output)

    gr.Markdown("### API Endpoints")
    gr.Markdown("- `POST /analyze`: Submit a repository for analysis")
    gr.Markdown("- `GET /report/{task_id}`: Retrieve analysis report")
    gr.Markdown("- `GET /health`: Check service health")

# Mount Gradio to the FastAPI app
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
