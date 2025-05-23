# GitHub Agent

A GitHub Pull Request agent that uses OpenAI's APIs for summarizing PRs, suggesting labels, and providing semantic search capabilities.

## Features

- Uses OpenAI's GPT models for PR summarization and label suggestions
- Uses OpenAI's text-embedding-ada-002 model for semantic search
- Integrates with Qdrant vector database for storing and searching PR embeddings
- Provides webhook endpoint for automated PR processing

## Architecture

The agent is split into three main components:

1. **LLM Agent** (`agents/llm_agent.py`)
   - Handles PR summarization and label suggestions
   - Uses OpenAI's GPT models via the official SDK
   - Configurable model selection (default: gpt-4)

2. **Embedding Agent** (`agents/embedding_agent.py`)
   - Handles semantic embeddings and similarity search
   - Uses OpenAI's text-embedding-ada-002 model
   - Integrates with Qdrant for vector storage and search
   - 1536-dimensional embeddings

3. **GitHub Agent** (`agents/github_agent.py`)
   - Handles GitHub API interactions
   - Posts comments on PRs
   - Manages PR metadata

## Setup

1. Install dependencies:
   ```bash
   make venv
   ```

2. Set up environment variables in `.env`:
   ```env
   OPENAI_API_KEY=your-openai-key           # Required
   GITHUB_TOKEN=your-github-token           # Required
   QDRANT_URL=http://localhost:6333         # Required
   COLLECTION_NAME=pr_cache                 # Optional, default: pr_cache
   OPENAI_MODEL=gpt-4                       # Optional, default: gpt-4
   ```

## Running

Start the FastAPI server:
```bash
make run
```

The server will listen for GitHub webhook events on `/webhook`.

## Testing

Run tests with coverage:
```bash
make test
```

## Configuration

All configuration is handled through environment variables in `config.py`. Key configurations:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GITHUB_TOKEN`: GitHub personal access token
- `QDRANT_URL`: URL of your Qdrant instance
- `COLLECTION_NAME`: Name of the Qdrant collection (default: 'pr_cache')
- `OPENAI_MODEL`: OpenAI model to use for summarization (default: 'gpt-4')

## Development

### Running Tests

```bash
make test
```

### Code Quality

```bash
make lint
make typecheck
```

### Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
3. Add tests
4. Run quality checks:
   ```bash
   make quality
   ```
5. Submit a PR

## CI/CD

GitHub Actions workflow runs on every PR and push to main:
- Runs tests
- Checks test coverage (minimum 80% required)
- Runs linting and type checking
- Requires OpenAI API key as a repository secret
