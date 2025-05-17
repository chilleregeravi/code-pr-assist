# Makefile for CAG PR Agent with venv and auto-install

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
UVICORN := $(VENV_DIR)/bin/uvicorn

.PHONY: venv run lint format clean test

venv:
	@test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: venv
	$(UVICORN) main:app --host 0.0.0.0 --port 8000 --reload

lint: venv
	$(VENV_DIR)/bin/black . && $(VENV_DIR)/bin/isort .

format: lint

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	rm -rf $(VENV_DIR)

test: venv
	PYTHONPATH=src $(VENV_DIR)/bin/pytest --cov=src --cov-report=term-missing tests/

lint:
	. .venv/bin/activate && black src tests && isort src tests

lint-check:
	. .venv/bin/activate && black --check src tests && isort --check-only src tests 