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

# Install Python dependencies for both subprojects
COPY ../database-agent/requirements.txt /tmp/database-agent-requirements.txt
COPY ../github-agent/requirements.txt /tmp/github-agent-requirements.txt

# Install Python packages
RUN pip install --upgrade pip && \
    pip install -r /tmp/database-agent-requirements.txt && \
    pip install -r /tmp/github-agent-requirements.txt

# Install additional dev tools and linters
RUN pip install \
    bandit \
    safety \
    black \
    isort \
    ruff \
    pre-commit \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock \
    httpx

# Set up Python path and environment
ENV PYTHONPATH=/workspaces/code-pr-assist
ENV PYTHONUNBUFFERED=1

# Set default workspace folder
WORKDIR /workspaces/code-pr-assist

# [Optional] Expose ports for the applications
EXPOSE 8000 8001 6333

# Create necessary directories
RUN mkdir -p /workspaces/code-pr-assist/.vscode

# Set up non-root user permissions
RUN chown -R vscode:vscode /workspaces
