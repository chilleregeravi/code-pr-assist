# Code PR Assist

AI-powered code analysis and PR assistance system with GitHub integration.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Git

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ravichillerega/code-pr-assist.git
   cd code-pr-assist
   ```

2. **Run the setup script:**
   ```bash
   ./setup-dev.sh
   ```

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

That's it! You're ready to develop.

## 🛠️ Development Commands

We use a unified Makefile for all development tasks:

```bash
# Show all available commands
make help

# Install dependencies
make install-dev

# Run all tests
make test

# Run specific agent tests
make test-github
make test-database

# Code quality
make lint          # Run linting (ruff only)
make format        # Format code (black, isort)

# Cleanup
make clean         # Remove cache files

# Run everything
make all           # Format, lint, test, and security checks
```

## 📁 Project Structure

```
code-pr-assist/
├── github-agent/          # GitHub integration agent
│   ├── src/
│   │   ├── github_agent/  # Main package
│   │   └── tests/         # Tests
│   ├── pyproject.toml     # Agent-specific config
│   └── Makefile          # Agent commands
├── database-agent/        # Database and vector store agent
│   ├── src/
│   │   ├── database_agent/ # Main package
│   │   └── tests/         # Tests
│   ├── pyproject.toml     # Agent-specific config
│   └── Makefile          # Agent commands
├── pyproject.toml         # Root project config
├── requirements.txt       # Unified dependencies
├── Makefile              # Unified commands
└── setup-dev.sh          # Development setup script
```

## 🔧 Configuration

All tool configurations are centralized in `pyproject.toml`:

- **Testing**: pytest with coverage
- **Linting**: ruff (fast, comprehensive linting)
- **Formatting**: black + isort (code formatting and import sorting)
- **Security**: bandit (security vulnerability scanning)
- **Pre-commit**: Automated code quality checks

**Note**: We've streamlined our pre-commit pipeline to avoid tool conflicts. Each tool has a specific role:
- **Black**: Code formatting (88-character lines)
- **isort**: Import sorting (black-compatible profile)
- **Ruff**: Fast linting (replaces flake8, pylint, etc.)
- **Bandit**: Security scanning

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage report
pytest --cov-report=html

# Run specific test files
pytest github-agent/src/tests/test_specific.py
```

## 📦 Dependencies

Dependencies are managed in three levels:

1. **Root `pyproject.toml`**: Shared dependencies and tool configurations
2. **Agent `pyproject.toml`**: Agent-specific dependencies
3. **Root `requirements.txt`**: Pinned versions for production

### Adding Dependencies

- **Shared dependencies**: Add to root `pyproject.toml`
- **Agent-specific**: Add to agent's `pyproject.toml`
- **Development tools**: Add to `[project.optional-dependencies.dev]`

## 🔒 Security

Security checks are integrated into the development workflow:

```bash
# Run security checks
make security

# Individual tools
bandit -r . -x tests/
safety check
```

## 🚀 Deployment

```bash
# Build packages
make build

# Install in production
pip install -e .
```

## 🤝 Contributing

1. **Setup development environment:**
   ```bash
   ./setup-dev.sh
   ```

2. **Make your changes**

3. **Run quality checks:**
   ```bash
   make all
   ```

4. **Commit your changes** (pre-commit hooks will run automatically)

5. **Submit a pull request**

### Code Quality Standards

- **Coverage**: Minimum 80% test coverage
- **Formatting**: Black + isort (automatic)
- **Linting**: Ruff (fast, includes many flake8 rules)
- **Security**: Bandit for security issues

## 📚 Architecture

### GitHub Agent
- Handles GitHub API interactions
- Processes pull requests
- Manages webhooks and events

### Database Agent
- Vector database operations (Qdrant)
- Embedding generation
- Data persistence and retrieval

### Shared Components
- OpenTelemetry tracing
- Common utilities
- Shared models and types

## 🔍 Troubleshooting

### Common Issues

1. **Import errors**: Make sure you've activated the virtual environment
   ```bash
   source .venv/bin/activate
   ```

2. **Test failures**: Ensure all dependencies are installed
   ```bash
   make install-dev
   ```

3. **Linting errors**: Run formatting first
   ```bash
   make format
   make lint
   ```

### Getting Help

- Check the [Issues](https://github.com/ravichillerega/code-pr-assist/issues) page
- Run `make help` for available commands
- Check individual agent READMEs for specific details

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
