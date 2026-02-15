# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    texlive-full \
    chktex \
    && rm -rf /var/lib/apt/lists/*

# Install uv and requirements as root
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -r requirements.txt && \
    uv pip install --system --no-cache-dir fastapi uvicorn gradio

# Create a non-root user and switch to it
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user/app

# Copy the rest of the application
# Force rebuild - 2026-02-15
COPY --chown=user . .

# Expose the port
EXPOSE 7860

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
