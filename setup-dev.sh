#!/bin/bash
# Development environment setup script for code-pr-assist

set -e

echo "🚀 Setting up code-pr-assist development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the project in development mode
echo "📚 Installing project dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Available commands:"
echo "  make help          - Show all available commands"
echo "  make test          - Run all tests"
echo "  make lint          - Run linting"
echo "  make format        - Format code"
echo "  make all           - Run format, lint, test, and security checks"
echo ""
echo "Happy coding! 🎉"
