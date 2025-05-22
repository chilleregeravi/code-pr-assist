# For use with GitHub Codespaces and Cursor
# See https://containers.dev/ for full reference

FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for both subprojects
COPY database-agent/requirements.txt /tmp/database-agent-requirements.txt
COPY github-agent/requirements.txt /tmp/github-agent-requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/database-agent-requirements.txt && \
    pip install -r /tmp/github-agent-requirements.txt

# Install additional dev tools (optional)
RUN pip install pytest mypy

# Set default workspace folder
WORKDIR /workspaces/code-pr-assist

# [Optional] Expose ports if your app runs a server
# EXPOSE 8000

# [Optional] Set up non-root user
# ARG USERNAME=dev
# RUN useradd -m $USERNAME && chown -R $USERNAME /workspaces
# USER $USERNAME
