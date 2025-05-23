# Code PR Assist Agent

A GitHub Pull Request assistant that uses LLMs (OpenAI or Ollama), Qdrant vector search, and GitHub API to summarize PRs, suggest labels, and comment automatically.

## Table of Contents

- [Features](#features)
- [Development Environment](#development-environment)
- [Requirements](#requirements)
- [Setup](#setup)
- [Running the Agent](#running-the-agent)
- [Running Tests](#running-tests)
- [Development Workflow](#development-workflow)
- [Continuous Integration](#continuous-integration)
- [Project Structure](#project-structure)
- [Database Agent](#database-agent)
- [Extending](#extending)
- [License](#license)
- [Pulling Docker Images from ghcr.io](#pulling-docker-images-from-ghcrio)

## Features

- Summarizes new PRs using OpenAI or Ollama LLMs
- Suggests labels based on similar past PRs
- Posts summary as a comment on the PR
- Stores PR embeddings in Qdrant for future similarity search
- Fully tested and CI-enabled
- **Complete DevContainer setup for consistent development environment**
- **Comprehensive VS Code configuration with Python tooling**

## Development Environment

This project includes a complete **DevContainer** configuration for a consistent, reproducible development environment that works with **GitHub Codespaces**, **VS Code Dev Containers**, and **Cursor IDE**.

### 🚀 Quick Start with DevContainer

1. **Prerequisites**: Install [VS Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in DevContainer**:
   ```bash
   git clone <repo-url>
   cd code-pr-assist
   code .
   ```
   - VS Code will prompt to "Reopen in Container" - click **Yes**
   - Or use Command Palette: `Dev Containers: Reopen in Container`

3. **GitHub Codespaces** (Alternative):
   - Click the green "Code" button → "Codespaces" → "Create codespace on main"
   - Everything will be automatically configured!

### 🛠️ DevContainer Features

The development environment includes:

#### **Python Development Stack**
- **Python 3.11** with pip and virtual environment support
- **Code Formatting**: Black formatter (88-character line length)
- **Import Sorting**: isort configured to work with Black
- **Linting**: flake8 for style checking
- **Type Checking**: mypy for static type analysis
- **Testing**: pytest with coverage support

#### **VS Code Extensions Pre-installed**
- **Python**: Core Python support with Pylance
- **Black Formatter**: Automatic code formatting
- **isort**: Import organization
- **flake8**: Python linting
- **MyPy Type Checker**: Static type checking
- **Jupyter**: Notebook support
- **GitHub Copilot**: AI code assistance (if available)
- **YAML Support**: For configuration files

#### **Development Tools**
- **pytest**: Testing framework with async support
- **mypy**: Static type checker
- **flake8**: Code linter
- **black**: Code formatter
- **isort**: Import organizer
- **pre-commit**: Git hooks for code quality

#### **Port Forwarding**
- **8000**: GitHub Agent API
- **8001**: Database Agent API
- **6333**: Qdrant Vector Database

#### **VS Code Tasks** (Access via `Ctrl+Shift+P` → "Tasks: Run Task")
- **Run GitHub Agent Tests**: Execute tests for the GitHub agent
- **Run Database Agent Tests**: Execute tests for the database agent
- **Format Code**: Format code using Black and organize imports
- **Lint Code**: Check code style with flake8
- **Type Check**: Static type checking with mypy
- **Start GitHub Agent**: Launch the GitHub agent service
- **Start Database Agent**: Launch the database agent service

#### **Debug Configurations**
- **GitHub Agent**: Debug the GitHub agent service
- **Database Agent**: Debug the database agent service
- **Python: Current File**: Debug any Python file
- **Python: Pytest**: Run tests in debug mode

### 🎯 Development Workflow

1. **Open project in DevContainer** (see Quick Start above)
2. **Environment auto-setup**: Dependencies installed automatically
3. **Start developing**: All tools configured and ready
4. **Run tests**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Run GitHub Agent Tests"
5. **Debug services**: Use F5 or debug configurations
6. **Code formatting**: Automatic on save, or use format tasks

### ⚙️ Configuration Details

The DevContainer configuration automatically:
- Installs all Python dependencies from both agents
- Configures Python interpreter and virtual environment
- Sets up linting, formatting, and type checking
- Configures debugging for both agents
- Sets up port forwarding for all services
- Applies proper VS Code settings for Python development

All configuration is **warning-free** and uses the latest VS Code Python extension formats.

## 🛡️ Security

This project includes comprehensive security scanning and monitoring:

### Security Features
- **CodeQL Analysis**: GitHub's semantic code analysis for vulnerabilities
- **Bandit**: Python-specific security linting
- **Semgrep**: Advanced static analysis for security patterns
- **Safety**: Dependency vulnerability scanning
- **Pre-commit hooks**: Automatic security checks before commits
- **Weekly security scans**: Automated via GitHub Actions

### Local Security Testing
Run a comprehensive security scan locally:
```bash
./.github/scripts/security-scan.sh
```

This will:
- Scan Python code for security vulnerabilities (Bandit)
- Check dependencies for known vulnerabilities (Safety)
- Run advanced security pattern detection (Semgrep)
- Generate detailed reports in `security-reports/`

### Scripts Location
All scripts are organized under `.github/scripts/`:
- `security-scan.sh` - Comprehensive security scanning
- `setup-labels.sh` - GitHub repository label setup

See [Security Policy](.github/security.md) for complete security documentation.

## Requirements

- Python 3.11+
- Access to OpenAI API or a running Ollama server
- Access to a Qdrant instance (local or remote)
- GitHub personal access token with repo permissions

## Setup

### Option 1: One-Command Setup (Fastest)
```bash
git clone <repo-url>
cd code-pr-assist
./setup.sh
```
This automatically:
- ✅ Sets up virtual environments for both agents
- ✅ Installs all dependencies
- ✅ Installs pre-commit hooks for automatic code quality checks
- ✅ Provides next steps

### Option 2: DevContainer (Recommended for Development)
Follow the [Development Environment](#development-environment) section above for the easiest setup.

### Option 3: Manual Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd code-pr-assist
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r database-agent/requirements.txt
   pip install -r github-agent/requirements.txt
   ```

4. **Set environment variables**
   Create `.env` files in both agent directories:

   **github-agent/.env**:
   ```env
   OPENAI_API_KEY=your-openai-key           # Required if using OpenAI
   GITHUB_TOKEN=your-github-token           # Required
   REPO_NAME=your-username/your-repo        # Required
   QDRANT_URL=http://localhost:6333         # Or your Qdrant instance
   COLLECTION_NAME=pr_cache                 # Optional, default: pr_cache
   OPENAI_MODEL=gpt-4                       # Optional, default: gpt-4
   LLM_PROVIDER=openai                      # 'openai' or 'ollama'
   OLLAMA_URL=http://localhost:11434        # If using Ollama
   OLLAMA_MODEL=llama2                      # If using Ollama
   ```

   **database-agent/.env**:
   ```env
   QDRANT_URL=http://localhost:6333         # Or your Qdrant instance
   COLLECTION_NAME=pr_cache                 # Optional, default: pr_cache
   ```

## Running the Agent

### DevContainer Environment
If using the DevContainer, use the pre-configured VS Code tasks:
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Start GitHub Agent"
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Start Database Agent"

### Manual Environment

1. **Start the GitHub Agent**

   ```bash
   cd github-agent
   make run
   # or
   source .venv/bin/activate
   uvicorn src.github_agent.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the Database Agent** (in another terminal)

   ```bash
   cd database-agent
   make run
   # or
   source .venv/bin/activate
   uvicorn src.database_agent.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Configure your GitHub repo webhook**
   - Set the webhook URL to `http://<your-server>:8000/webhook`
   - Content type: `application/json`
   - Trigger: Pull requests

## Running Tests

### DevContainer Environment
Use VS Code tasks:
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Run GitHub Agent Tests"
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Database Agent Tests"

### Manual Environment
```bash
# Test GitHub Agent
cd github-agent
make test

# Test Database Agent
cd database-agent
make test
```

**Current Test Status**: All 41 tests passing with 97% coverage ✅

## Development Workflow

### Code Quality Tools

The project includes comprehensive code quality tools:

#### **Formatting and Linting**
```bash
# Format code (DevContainer: use Format tasks)
make format

# Check linting (DevContainer: use Lint tasks)
make lint

# Type checking (DevContainer: use Type Check tasks)
make type-check
```

#### **Git Hooks**
Pre-commit hooks are configured to automatically:
- Format code with Black
- Sort imports with isort
- Run flake8 linting
- Run tests with full coverage
- Check for merge conflicts and code quality

**Automatic Installation** (Recommended):
```bash
# One-command setup for everything
./setup.sh

# Or setup individual agents with pre-commit hooks
cd github-agent && make setup
cd database-agent && make setup
```

**Manual Installation**:
```bash
pip install pre-commit
pre-commit install
```

#### **Available Make Commands**
```bash
make setup         # Setup environment + install pre-commit hooks
make test          # Run tests with coverage
make lint          # Run flake8 linting
make format        # Format with Black and isort
make type-check    # Run mypy type checking
make clean         # Clean up cache files
make venv          # Create virtual environment only
make run           # Start the service
```

## Continuous Integration

- GitHub Actions is set up to run tests and coverage on every push/PR to `main`.
- All tests must pass and coverage must be maintained
- Code formatting and linting are automatically checked

## Project Structure

```
code-pr-assist/
├── .devcontainer/              # DevContainer configuration
│   ├── devcontainer.json      # Main devcontainer config
│   ├── Dockerfile             # Container image definition
│   └── README.md              # DevContainer documentation
├── .vscode/                    # VS Code configuration
│   ├── settings.json          # Workspace settings
│   ├── settings.template.json # Template for extension-dependent settings
│   ├── launch.json            # Debug configurations
│   └── tasks.json             # Development tasks
├── database-agent/             # Handles PR data validation, transformation, and storage in Qdrant
├── github-agent/               # Handles GitHub API interactions and PR event processing
├── docs/                       # Documentation files
├── .github/                    # GitHub workflows and configurations
├── .gitignore                  # Git ignore file
├── .flake8                     # Flake8 configuration
├── mypy.ini                    # MyPy configuration
├── pytest.ini                 # Pytest configuration
├── pyproject.toml              # Project metadata
├── Makefile.common             # Common dev commands for all agents
├── CONTRIBUTING.md             # Contribution guidelines
└── LICENSE                     # License file
```

## Database Agent

The **database-agent** is responsible for validating, transforming, and storing pull request (PR) data in a Qdrant vector database. It provides:
- Data validation and transformation utilities for PRs
- Batch and single PR processing
- Integration with Qdrant for vector storage and search
- Utilities for deleting, searching, and retrieving PRs

### Setup

1. Navigate to the `database-agent` directory:
   ```bash
   cd database-agent
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Development Commands

- **Run lint and formatting checks:**
  ```bash
  make -f ../Makefile.common lint-check-all
  ```
- **Run tests:**
  ```bash
  make -f ../Makefile.common test
  ```
- **Auto-format code:**
  ```bash
  make -f ../Makefile.common format
  ```
- **Type checking:**
  ```bash
  source .venv/bin/activate
  mypy src
  ```

### Usage

The database-agent is designed to be used as a library/module by other agents (such as the GitHub agent) or as part of a larger workflow. See the code in `database-agent/src/database_agent/` for entry points and API.

## Extending

- Add new LLM providers by extending `llm_utils.py`.
- Add new vector search or storage backends by extending `qdrant_utils.py`.
- All development tools are pre-configured in the DevContainer for easy extension development

## License

See [LICENSE](LICENSE).

## Pulling Docker Images from ghcr.io

You can pull the Docker images for `database-agent` and `github-agent` from the GitHub Container Registry (ghcr.io) using the following commands:

### Database Agent

```bash
docker pull ghcr.io/chilleregeravi/database-agent:latest
```

### GitHub Agent

```bash
docker pull ghcr.io/chilleregeravi/github-agent:latest
```
