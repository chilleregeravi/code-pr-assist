# Development Environment Setup

This document provides a comprehensive guide to setting up and working with the Code PR Assist development environment, including our streamlined tooling configuration.

## 🚀 Quick Setup

```bash
git clone https://github.com/ravichillerega/code-pr-assist.git
cd code-pr-assist
./setup-dev.sh
source .venv/bin/activate
```

## 🛠️ Tool Configuration

We've optimized our development pipeline to avoid tool conflicts and provide fast, reliable code quality checks.

### VS Code Configuration

The project includes multiple `.vscode` folders for different development contexts:

#### Root Workspace (`./.vscode/`)
- **Purpose**: Workspace-level configuration for the entire project
- **When to use**: Opening the root `code-pr-assist` folder in VS Code
- **Contains**: Debug configurations, workspace tasks, multi-agent Python paths
- **Interpreter**: `./.venv/bin/python` (root virtual environment)

#### Agent-Specific (`./github-agent/.vscode/`, `./database-agent/.vscode/`)
- **Purpose**: Agent-specific development environment
- **When to use**: Working on individual agents in isolation
- **Contains**: Agent-specific Python paths, local virtual environment settings
- **Interpreter**: `./.venv/bin/python` (agent-specific virtual environment)

**All configurations are updated to use our streamlined tooling** (Black, isort, Ruff, no flake8/mypy linting).

### Pre-commit Hooks (Automatic)

The following tools run automatically on every commit:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Black** | Code formatting | 88-character lines, Python 3.11+ |
| **isort** | Import sorting | Black-compatible profile |
| **Ruff** | Linting | Fast replacement for flake8, pylint, etc. |
| **Bandit** | Security scanning | Configured in pyproject.toml |
| **pre-commit-hooks** | Basic file checks | Trailing whitespace, YAML validation, etc. |

### Manual Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **MyPy** | Type checking | Before PRs, complex refactoring |
| **pytest** | Testing | Development, CI/CD |

## 🔧 Tool Responsibilities

### Why This Configuration?

We've carefully chosen tools that work together without conflicts:

- **Single formatter**: Only Black handles code formatting (no ruff-format)
- **Single import sorter**: Only isort handles imports (ruff import rules disabled)
- **Fast linting**: Ruff replaces multiple slower tools (flake8, pylint, pycodestyle)
- **Optional type checking**: MyPy available manually (not in pre-commit for setup simplicity)

### Removed from Pre-commit

- **MyPy**: Too strict for current codebase, causes setup friction
- **ruff-format**: Conflicts with Black formatting
- **Test running**: Tests run in CI, not needed for every commit

## 📋 Development Commands

```bash
# Code quality (automatic on commit)
make format     # Black + isort formatting
make lint       # Ruff linting only
make type-check # MyPy type checking (manual)

# Testing
make test            # Run all tests
make test-github     # GitHub agent tests only
make test-database   # Database agent tests only

# Project management
make install-dev     # Install dev dependencies + pre-commit
make clean          # Remove cache files
make security       # Bandit security scan
make all           # format + lint + test + security
```

## 🎯 Code Quality Standards

### Automatic (Pre-commit)
- **Formatting**: Black (88 chars, trailing commas, etc.)
- **Import sorting**: isort (black profile, first-party detection)
- **Linting**: Ruff (E, W, F, C, B, UP, N, S, RUF rules)
- **Security**: Bandit (excluding tests, configured skips)

### Manual (Before PRs)
- **Type checking**: MyPy (strict mode configured)
- **Test coverage**: 80% minimum (pytest-cov)
- **Documentation**: Docstrings for public APIs

## 🔍 Configuration Details

### pyproject.toml Highlights

```toml
[tool.ruff.lint]
ignore = [
    "I001",  # import sorting (handled by isort)
    "C901",  # complex-structure (acceptable complexity)
    "S101",  # assert statements (OK in tests)
]

[tool.isort]
profile = "black"  # Compatible with Black
known_first_party = ["github_agent", "database_agent"]

[tool.bandit]
exclude_dirs = ["tests"]  # Security rules relaxed for tests
```

### Pre-commit Configuration

```yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        # Note: NO ruff-format hook

  - repo: https://github.com/PyCQA/bandit
    hooks:
      - id: bandit
```

## 🚨 Troubleshooting

### Common Issues

**Pre-commit hooks not running?**
```bash
pre-commit install
```

**Formatting conflicts between tools?**
- We've eliminated these - only Black handles formatting
- Only isort handles imports
- Ruff only does linting (no formatting/import rules)

**MyPy errors?**
```bash
# MyPy is optional - run manually when needed
make type-check

# Or skip for now - it's not required for commits
```

**Ruff vs Black conflicts?**
- Shouldn't happen - we ignore E501 (line length) in ruff
- Black handles all formatting, ruff only does linting

### Performance

- **Pre-commit runs in ~5-10 seconds** (vs previous 30+ seconds)
- **Ruff is 10-100x faster** than flake8/pylint
- **No mypy delays** during commits

## 🔄 Migration from Previous Setup

If you're updating from an older version:

```bash
# 1. Update pre-commit
pre-commit uninstall
pre-commit install

# 2. Clear caches
make clean

# 3. Run once to verify
make all
```

### Changes Made

- ✅ **Removed**: mypy from pre-commit (too strict)
- ✅ **Removed**: ruff-format (conflicts with Black)
- ✅ **Added**: Clearer tool responsibilities
- ✅ **Added**: Faster execution times
- ✅ **Added**: Better error messages

## 📚 References

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [pre-commit Documentation](https://pre-commit.com/)

## 🎉 Success Indicators

After setup, you should see:

```bash
$ make all
✓ Black formatting: passed
✓ isort import sorting: passed
✓ Ruff linting: passed
✓ All tests: passed (12 tests)
✓ Security scan: passed
✅ All checks passed!

$ git commit -m "test"
Trim Trailing Whitespace.............................................Passed
Fix End of Files.....................................................Passed
Check Yaml...........................................................Passed
Check for added large files..........................................Passed
Check for merge conflicts............................................Passed
Debug Statements (Python)...........................................Passed
black................................................................Passed
isort................................................................Passed
ruff.................................................................Passed
bandit...............................................................Passed
```

This indicates your development environment is properly configured and ready for development!
