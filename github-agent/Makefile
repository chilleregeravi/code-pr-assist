include ../Makefile.common

test:
	. .venv/bin/activate && \
	pip install -e ".[test]" && \
	pytest -v --cov=src/github_agent --cov-report=term-missing --cov-report=xml:coverage.xml
