# For use with GitHub Codespaces and Cursor
# See https://containers.dev/ for full reference

FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    vim \
    nano \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files for both projects
COPY ../database-agent/requirements.txt /tmp/database-agent-requirements.txt
COPY ../database-agent/requirements-dev.txt /tmp/database-agent-requirements-dev.txt
COPY ../github-agent/requirements.txt /tmp/github-agent-requirements.txt
COPY ../github-agent/requirements-dev.txt /tmp/github-agent-requirements-dev.txt

# Install Python packages (main and dev dependencies)
RUN pip install --upgrade pip && \
    pip install -r /tmp/database-agent-requirements.txt && \
    pip install -r /tmp/database-agent-requirements-dev.txt && \
    pip install -r /tmp/github-agent-requirements.txt && \
    pip install -r /tmp/github-agent-requirements-dev.txt

# Set up Python path and environment
ENV PYTHONPATH=/workspaces/code-pr-assist
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set default workspace folder
WORKDIR /workspaces/code-pr-assist

# [Optional] Expose ports for the applications
EXPOSE 8000 8001 6333

# Create necessary directories
RUN mkdir -p /workspaces/code-pr-assist/.vscode

# Set up non-root user permissions
RUN chown -R vscode:vscode /workspaces
