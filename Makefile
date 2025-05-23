# Unified Makefile for code-pr-assist project
.PHONY: help install install-dev test test-github test-database lint format clean build docs security-check all

PYTHON := python3
PIP := pip

# Default target
help:
	@echo "Available commands:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-github   - Run GitHub agent tests"
	@echo "  test-database - Run database agent tests"
	@echo "  lint          - Run linting (ruff only)"
	@echo "  format        - Format code (black, isort)"
	@echo "  clean         - Clean up cache and temp files"
	@echo "  build         - Build packages"
	@echo "  docs          - Build documentation"
	@echo "  security      - Run security checks"
	@echo "  all           - Run format, lint, test, security"

# Installation
install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"
	$(PIP) install pre-commit
	pre-commit install

# Testing
test:
	pytest

test-github:
	cd github-agent && $(PYTHON) -m pytest

test-database:
	cd database-agent && $(PYTHON) -m pytest

# Code quality
lint:
	ruff check .

format:
	black .
	isort .

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
	rm -rf htmlcov/ coverage.xml build/ dist/

# Build
build: clean
	$(PYTHON) -m build

# Documentation
docs:
	@echo "Documentation will be built here when mkdocs is configured"

# Security
security:
	bandit -r . -x tests/,test_*.py
	safety check

# Run everything
all: format lint test security
	@echo "✅ All checks passed!"

# Legacy support for existing workflow
venv:
	@echo "⚠️  venv target is deprecated. Use 'make install-dev' instead."
	make install-dev
