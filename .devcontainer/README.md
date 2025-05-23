# Development Container Setup

This development container is configured for Python development with GitHub Codespaces and Cursor IDE support.

## Features

### Python Development Environment
- **Python 3.11** with pip and virtual environment support
- **Code Formatting**: Black formatter with 88-character line length
- **Import Sorting**: isort configured to work with Black
- **Linting**: Ruff for fast, comprehensive code checking
- **Testing**: pytest with coverage support

### VS Code Extensions Included
- **Python**: Core Python support
- **Pylance**: Advanced Python language features
- **Ruff**: Fast Python linting
- **Black Formatter**: Code formatting
- **isort**: Import sorting
- **Jupyter**: Notebook support
- **Test Adapter**: Enhanced testing support
- **YAML**: YAML file support
- **GitHub Copilot**: AI code assistance (if available)

### Pre-configured Development Tools
- **pytest**: Testing framework with async support
- **ruff**: Fast code linter
- **black**: Code formatter
- **isort**: Import organizer
- **pre-commit**: Git hooks for code quality

### Port Forwarding
- **8000**: GitHub Agent API
- **8001**: Database Agent API
- **6333**: Qdrant Vector Database

### Development Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- **Run GitHub Agent Tests**: Execute tests for the GitHub agent
- **Run Database Agent Tests**: Execute tests for the database agent
- **Format GitHub Agent Code**: Format code using Black
- **Format Database Agent Code**: Format code using Black
- **Sort GitHub Agent Imports**: Organize imports using isort
- **Sort Database Agent Imports**: Organize imports using isort
- **Lint GitHub Agent**: Check code style with ruff
- **Lint Database Agent**: Check code style with ruff
- **Start GitHub Agent**: Launch the GitHub agent service
- **Start Database Agent**: Launch the database agent service

### Debug Configurations
- **GitHub Agent**: Debug the GitHub agent service
- **Database Agent**: Debug the database agent service
- **Python: Current File**: Debug the currently open Python file
- **Python: Pytest**: Run tests in debug mode

## Getting Started

1. **Open in Codespaces/Cursor**: The container will automatically build and install dependencies
2. **Environment Setup**: Create `.env` files in each agent directory with your API keys
3. **Run Tests**: Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Run GitHub Agent Tests"
4. **Start Development**: Use the debug configurations or tasks to start the services

## Environment Variables

The container includes these development environment variables:
- `PYTHONPATH`: Set to workspace root
- `PYTHONUNBUFFERED`: Ensures real-time output
- `PYTHONDONTWRITEBYTECODE`: Prevents .pyc file creation

## Configuration Highlights

### Modern Python Extension Settings
- Uses the latest VS Code Python extension configuration format
- Separate configurations for each tool (black-formatter, ruff, isort)
- Language-specific formatting settings for Python files
- Proper problem matchers for better error reporting

### Improved Task Management
- Individual tasks for linting
- Proper working directory configuration
- Enhanced problem matchers for ruff
- Task dependencies for formatting workflows

### Container Features
- Docker-in-Docker support for container development
- Git integration with proper mounting
- Qdrant port forwarding for vector database development

## File Structure

```
.devcontainer/
├── devcontainer.json      # Main devcontainer configuration
├── Dockerfile            # Container image definition
└── README.md            # This file

.vscode/
├── settings.json         # VS Code workspace settings
├── launch.json          # Debug configurations
└── tasks.json           # Development tasks
```

## Customization

You can customize the development environment by:
1. Modifying `.devcontainer/devcontainer.json` for container settings
2. Updating `.vscode/settings.json` for editor preferences
3. Adding new tasks in `.vscode/tasks.json`
4. Creating new debug configurations in `.vscode/launch.json`

## Troubleshooting

### Common Issues
- **Extensions not loading**: Reload the window with `Ctrl+Shift+P` → "Developer: Reload Window"
- **Python not found**: Check that the interpreter path is set correctly in settings
- **Tests not discovered**: Ensure pytest is installed and the workspace folder is correct
- **Linting not working**: Verify that ruff is installed and configured

### Extension Updates
This configuration uses the latest VS Code Python extension format. If you see warnings about deprecated settings, the configuration has been updated to use:
- `[python]` language-specific settings instead of global `python.formatting.*`
- Individual extension settings like `black-formatter.args` instead of deprecated options
- Explicit action types like `"source.organizeImports": "explicit"`
