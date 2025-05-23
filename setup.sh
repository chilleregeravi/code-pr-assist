#!/bin/bash
set -e

echo "🚀 Setting up Code PR Assist development environment..."

# Check if we're in the right directory
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "❌ Error: Please run this script from the root of the code-pr-assist repository"
    exit 1
fi

# Function to setup an agent
setup_agent() {
    local agent_name=$1
    echo "📦 Setting up $agent_name..."

    cd "$agent_name"

    # Create virtual environment and install dependencies
    if [ -f "Makefile" ]; then
        make setup
    else
        echo "⚠️  No Makefile found for $agent_name, setting up manually..."
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
        fi
        source .venv/bin/activate
        pip install --upgrade pip
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
        pip install pre-commit
        pre-commit install
    fi

    cd ..
    echo "✅ $agent_name setup complete"
}

# Install pre-commit globally (fallback)
echo "📋 Installing pre-commit globally..."
pip install --user pre-commit 2>/dev/null || pip3 install --user pre-commit 2>/dev/null || {
    echo "⚠️  Could not install pre-commit globally. Installing locally instead."
}

# Setup GitHub Agent
if [ -d "github-agent" ]; then
    setup_agent "github-agent"
else
    echo "⚠️  github-agent directory not found"
fi

# Setup Database Agent
if [ -d "database-agent" ]; then
    setup_agent "database-agent"
else
    echo "⚠️  database-agent directory not found"
fi

# Install pre-commit hooks at root level
echo "🔧 Installing pre-commit hooks at repository root..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed successfully!"
else
    echo "❌ pre-commit command not found. Please install pre-commit manually:"
    echo "   pip install pre-commit"
    echo "   pre-commit install"
fi

echo ""
echo "🎉 Setup complete! Your development environment is ready."
echo ""
echo "📝 Next steps:"
echo "   1. Start GitHub Agent: cd github-agent && make run"
echo "   2. Start Database Agent: cd database-agent && make run"
echo "   3. Make changes and commit - pre-commit hooks will run automatically!"
echo ""
echo "🔧 Available commands:"
echo "   make test     - Run tests"
echo "   make format   - Format code"
echo "   make lint     - Check code quality"
echo ""
