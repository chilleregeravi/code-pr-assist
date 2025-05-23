# Contributing to Code PR Assist

Thank you for your interest in contributing to the Code PR Assist project! This guide will help you get set up quickly and contribute effectively to our GitHub Agent and Database Agent.

## 🚀 Quick Start

### Option 1: One-Command Setup (Fastest)
```bash
git clone https://github.com/your-org/code-pr-assist.git
cd code-pr-assist
./setup.sh
```

### Option 2: Per-Agent Setup
```bash
# Setup GitHub Agent
cd github-agent
make setup

# Setup Database Agent
cd ../database-agent
make setup
```

### Option 3: DevContainer (Recommended for VS Code Users)
1. Open the project in VS Code
2. Click "Reopen in Container" when prompted
3. Everything is automatically configured!

### Option 4: Manual Setup
```bash
# Install pre-commit globally
pip install pre-commit

# Clone and setup
git clone https://github.com/your-org/code-pr-assist.git
cd code-pr-assist
pre-commit install

# Setup agents individually
cd github-agent && make venv
cd ../database-agent && make venv
```

## 🛠️ Development Environment

We provide multiple development environment options:

### DevContainer (Recommended)
- **Complete Python 3.11 environment** with all tools pre-configured
- **VS Code extensions** for Python, Black, isort, Ruff
- **Automatic dependency installation** and environment setup
- **Pre-commit hooks** installed automatically
- **Port forwarding** for all services (8000, 8001, 6333)
- **Debug configurations** for both agents

### Manual Environment
- **Python 3.11+** required
- **Virtual environments** for each agent
- **Manual dependency installation** from requirements.txt
- **Manual pre-commit setup** required

## ✅ Code Quality (Automated)

Our development workflow includes **automatic code quality checks** that run before every commit:

### Pre-commit Hooks
When you commit code, these checks run automatically:
- ✅ **Black formatting** (88-character line length)
- ✅ **isort import sorting** (compatible with Black)
- ✅ **Ruff linting** (fast, comprehensive style and quality checks)
- ✅ **Bandit security scanning** (security vulnerability detection)
- ✅ **Basic file checks** (trailing whitespace, merge conflicts, YAML validation)

**Note**: Our pre-commit pipeline is optimized to avoid tool conflicts:
- **No duplicate formatting**: Only Black handles code formatting
- **No import conflicts**: Only isort handles import sorting
- **Fast execution**: Ruff replaces multiple slower tools

### Verification
After setup, test that pre-commit works:
```bash
# Make a small change
echo "# Test" >> README.md
git add README.md
git commit -m "test: Verify pre-commit hooks"

# You should see output like:
# Trim Trailing Whitespace.............................................Passed
# Fix End of Files...................................................Passed
# Check Yaml.........................................................Passed
# Check for added large files........................................Passed
# Check for merge conflicts..........................................Passed
# Debug Statements (Python)..........................................Passed
# black..............................................................Passed
# isort..............................................................Passed
# ruff...............................................................Passed
# bandit.............................................................Passed
```

## 🧪 Testing

### Running Tests
```bash
# Test GitHub Agent
cd github-agent && make test

# Test Database Agent
cd database-agent && make test

# Or run specific test files
cd github-agent
source .venv/bin/activate
pytest src/tests/test_main.py -v
```

### Test Requirements
- **All tests must pass** before committing
- **Maintain 80%+ coverage** (currently at 86%)
- **Add tests for new features**
- **Update tests when modifying existing code**

### Writing Tests
- Use `pytest` framework with `pytest-asyncio` for async tests
- Mock external dependencies (OpenAI, GitHub API, Qdrant)
- Follow existing test patterns in `src/tests/`
- Include both positive and negative test cases

## 🎨 Code Style

### Automatic Formatting
Code is automatically formatted on commit, but you can run manually:
```bash
# Format code
cd github-agent
make format  # or: black src/ && isort src/

# Check formatting without applying
black --check --diff src/
isort --check-only --diff src/
```

### Style Guidelines
- **PEP 8 compliance** enforced by flake8
- **88-character line length** (Black standard)
- **Type annotations** for all function parameters and return values
- **Docstrings** for classes and public methods
- **Consistent import ordering** (standard, third-party, local)

### Code Quality Tools
- **Black**: Automatic code formatting (88-character lines)
- **isort**: Import sorting and organization (black-compatible)
- **Ruff**: Fast linting (replaces flake8, pylint, pycodestyle, etc.)
- **Bandit**: Security vulnerability scanning
- **pytest**: Testing framework with coverage reporting

## 📝 Development Workflow

### 1. Setup Environment
Choose one of the setup options above. We recommend:
- **DevContainer** for VS Code users
- **./setup.sh** for command-line users

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Develop
- Write code following our style guidelines
- Add tests for new functionality
- Run tests frequently: `make test`

### 4. Commit Changes
```bash
git add .
git commit -m "feat: Your descriptive commit message"
# Pre-commit hooks run automatically!
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

## 🔧 Available Commands

### Common Commands
```bash
make setup         # Setup environment + install pre-commit hooks
make test          # Run tests with coverage
make format        # Format code with Black and isort
make lint          # Check code style with ruff
make clean         # Clean up cache files
make run           # Start the service
```

### Development Tasks (VS Code)
If using DevContainer, access via `Ctrl+Shift+P` → "Tasks: Run Task":
- **Run GitHub Agent Tests**
- **Run Database Agent Tests**
- **Format Code**
- **Lint Code**
- **Type Check**
- **Start GitHub Agent**
- **Start Database Agent**

## 📋 Pull Request Guidelines

### Before Submitting
- ✅ **All tests pass** (automatic via pre-commit)
- ✅ **Code is formatted** (automatic via pre-commit)
- ✅ **No linting errors** (automatic via pre-commit)
- ✅ **New tests added** for new functionality
- ✅ **Documentation updated** if needed

### PR Description
Include:
- **Clear description** of changes
- **Link to related issues** (#123)
- **Testing notes** if applicable
- **Breaking changes** if any

### Example PR Title Formats
- `feat: Add new LLM provider support`
- `fix: Resolve timeout issue in embedding agent`
- `docs: Update API documentation`
- `test: Add integration tests for webhook`
- `refactor: Improve error handling`

## 🐛 Reporting Issues

### Bug Reports
Include:
- **Python version** and environment details
- **Exact error message** and stack trace
- **Steps to reproduce** the issue
- **Expected vs actual behavior**

### Feature Requests
Include:
- **Use case description**
- **Proposed solution** (if any)
- **Alternative approaches** considered

## 🏗️ Project Structure

```
code-pr-assist/
├── github-agent/           # GitHub API interactions & PR processing
│   ├── src/github_agent/  # Main application code
│   ├── src/tests/         # Test files
│   └── requirements.txt   # Dependencies
├── database-agent/         # Data validation & Qdrant storage
│   ├── src/database_agent/ # Main application code
│   ├── src/tests/         # Test files
│   └── requirements.txt   # Dependencies
├── .devcontainer/         # VS Code DevContainer config
├── .github/               # GitHub Actions CI/CD
├── .pre-commit-config.yaml # Pre-commit hook configuration
├── setup.sh               # One-command setup script
└── Makefile.common        # Shared development commands
```

## 🆘 Getting Help

### Common Issues
- **Pre-commit hooks not running?** → Run `pre-commit install`
- **Tests failing?** → Check `make test` output for specific errors
- **Import errors?** → Ensure virtual environment is activated
- **Port conflicts?** → Check if services are already running

### Where to Ask
- **GitHub Issues**: Bug reports and feature requests
- **Pull Request Comments**: Code-specific questions
- **README.md**: General usage and setup questions

## 🎯 Tips for Success

1. **Start small**: Begin with minor improvements or bug fixes
2. **Read existing code**: Understand patterns before adding new features
3. **Test thoroughly**: Both unit tests and manual testing
4. **Ask questions**: Don't hesitate to ask for clarification
5. **Follow conventions**: Stick to established patterns and styles

## 🔄 Continuous Integration

Our CI pipeline automatically:
- ✅ **Runs all tests** on multiple Python versions
- ✅ **Checks code formatting** with Black and isort
- ✅ **Validates code quality** with flake8
- ✅ **Measures test coverage** (must maintain 80%+)
- ✅ **Builds Docker images** for deployment

All checks must pass before merging!

---

Thank you for contributing to Code PR Assist! Your contributions help make PR review automation better for everyone. 🚀
