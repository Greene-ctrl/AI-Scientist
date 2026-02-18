# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=.:CriticalThinking

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv and requirements
COPY CriticalThinking/requirements.txt .
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -r requirements.txt && \
    uv pip install --system --no-cache-dir gradio uvicorn

# Create a non-root user and switch to it
# Hugging Face Spaces use a user with UID 1000
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user/app

# Copy the rest of the application
# Use --chown=user to ensure the user has permissions
COPY --chown=user . .

# Expose the port
EXPOSE 7860

# Command to run the application
# We use uvicorn to run the hf_app:app
CMD ["uvicorn", "hf_app:app", "--host", "0.0.0.0", "--port", "7860"]
