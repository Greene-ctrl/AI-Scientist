import os
import subprocess
import threading
import time
import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store process state
current_process = None
process_output = ""

class RunRequest(BaseModel):
    model: str
    experiment: str
    num_ideas: int
    openai_key: Optional[str] = None
    anthropic_key: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run_api(req: RunRequest):
    return {"message": start_scientist(req.model, req.experiment, req.num_ideas, req.openai_key, req.anthropic_key)}

@app.get("/logs")
def get_logs():
    return {"logs": process_output}

def run_scientist_cmd(model, experiment, num_ideas, openai_key, anthropic_key):
    global current_process, process_output
    process_output = "--- Starting AI Scientist ---\n"

    env = os.environ.copy()
    if openai_key:
        env["OPENAI_API_KEY"] = openai_key
    if anthropic_key:
        env["ANTHROPIC_API_KEY"] = anthropic_key

    cmd = [
        "python", "launch_scientist.py",
        "--model", model,
        "--experiment", experiment,
        "--num-ideas", str(int(num_ideas))
    ]

    process_output += f"Running command: {' '.join(cmd)}\n\n"

    try:
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env
        )

        for line in current_process.stdout:
            process_output += line
            # Keep only the last 50000 characters to avoid memory issues
            if len(process_output) > 50000:
                process_output = process_output[-50000:]

        current_process.wait()
        process_output += f"\n--- Process finished with return code {current_process.returncode} ---\n"
    except Exception as e:
        process_output += f"\nError: {str(e)}\n"
    finally:
        current_process = None

def start_scientist(model, experiment, num_ideas, openai_key, anthropic_key):
    global current_process
    if current_process is not None:
        return "A process is already running."

    thread = threading.Thread(target=run_scientist_cmd, args=(model, experiment, num_ideas, openai_key, anthropic_key))
    thread.start()
    return "Process started."

def get_output():
    return process_output

def stop_process():
    global current_process
    if current_process:
        current_process.terminate()
        return "Process termination requested."
    return "No process running."

def list_results():
    results = []
    if os.path.exists("results"):
        for root, dirs, files in os.walk("results"):
            for file in files:
                if file.endswith(".pdf"):
                    results.append(os.path.join(root, file))
    return results

with gr.Blocks(title="The AI Scientist") as demo:
    gr.Markdown("# 🧑‍🔬 The AI Scientist")
    gr.Markdown("Fully Automated Open-Ended Scientific Discovery")

    with gr.Row():
        with gr.Column():
            model_input = gr.Dropdown(
                choices=[
                    "gpt-4o-2024-05-13",
                    "claude-3-5-sonnet-20241022",
                    "gpt-4o-mini",
                    "deepseek-chat",
                    "deepseek-reasoner"
                ],
                label="Model",
                value="gpt-4o-2024-05-13"
            )
            exp_input = gr.Dropdown(
                choices=[
                    "nanoGPT",
                    "nanoGPT_lite",
                    "2d_diffusion",
                    "grokking"
                ],
                label="Experiment Template",
                value="nanoGPT_lite"
            )
            num_ideas_input = gr.Slider(minimum=1, maximum=10, step=1, value=1, label="Number of Ideas")

        with gr.Column():
            openai_key_input = gr.Textbox(label="OpenAI API Key (Required for GPT models)", type="password")
            anthropic_key_input = gr.Textbox(label="Anthropic API Key (Required for Claude models)", type="password")

    with gr.Row():
        run_btn = gr.Button("🚀 Run AI Scientist", variant="primary")
        stop_btn = gr.Button("🛑 Stop", variant="danger")
        refresh_btn = gr.Button("🔄 Refresh Output")

    output_text = gr.Textbox(label="Logs", interactive=False, lines=15, max_lines=25)

    with gr.Accordion("Generated Papers", open=False):
        results_list = gr.File(label="PDF Papers", file_count="multiple")
        refresh_results_btn = gr.Button("Refresh Results List")

    # Event handlers
    run_btn.click(start_scientist, inputs=[model_input, exp_input, num_ideas_input, openai_key_input, anthropic_key_input], outputs=output_text)
    stop_btn.click(stop_process, None, output_text)
    refresh_btn.click(get_output, None, output_text)
    refresh_results_btn.click(list_results, None, results_list)

    # Auto-refresh logs every 3 seconds
    try:
        timer = gr.Timer(3)
        timer.tick(get_output, None, output_text)
    except:
        demo.load(get_output, None, output_text)

# Mount Gradio to FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
