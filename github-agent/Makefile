include ../Makefile.common

# Override the test target to set PYTHONPATH
.PHONY: test

test:
	PYTHONPATH=src $(VENV_ACTIVATE)
	PYTHONPATH=src .venv/bin/pytest -c ../pytest.ini -vv