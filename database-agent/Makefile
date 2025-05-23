include ../Makefile.common

test:
	. .venv/bin/activate && \
	pip install -e . && \
	pip install -r requirements-test.txt && \
	pytest -v --cov=src/database_agent --cov-report=term-missing --cov-report=xml:coverage.xml
