# Code PR Assist Agent

A GitHub Pull Request assistant that uses LLMs (OpenAI or Ollama), Qdrant vector search, and GitHub API to summarize PRs, suggest labels, and comment automatically.

## Features

- Summarizes new PRs using OpenAI or Ollama LLMs
- Suggests labels based on similar past PRs
- Posts summary as a comment on the PR
- Stores PR embeddings in Qdrant for future similarity search
- Fully tested and CI-enabled

## Requirements

- Python 3.11+
- Access to OpenAI API or a running Ollama server
- Access to a Qdrant instance (local or remote)
- GitHub personal access token with repo permissions

## Setup

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
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   Create a `.env` file or export these variables:

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

## Running the Agent

1. **Start the FastAPI server**

   ```bash
   make run
   # or
   source .venv/bin/activate
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Configure your GitHub repo webhook**
   - Set the webhook URL to `http://<your-server>:8000/webhook`
   - Content type: `application/json`
   - Trigger: Pull requests

## Running Tests

```bash
make test
```

- This will run all tests and show a coverage report.

## Continuous Integration

- GitHub Actions is set up to run tests and coverage on every push/PR to `main`.

## Project Structure

```
code-pr-assist/
  database-agent/         # Handles PR data validation, transformation, and storage in Qdrant
  github-agent/           # Handles GitHub API interactions and PR event processing
  src/agent/              # Main agent code (legacy or shared)
  tests/                  # All test files
  requirements.txt        # Python dependencies
  Makefile.common         # Common dev commands for all agents
  .github/workflows/      # CI pipeline
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

## License

See [LICENSE](LICENSE).
