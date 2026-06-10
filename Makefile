PYTHON ?= python

.PHONY: install format lint test run-smoke run-pipeline app

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check . --fix

lint:
	$(PYTHON) -m ruff format . --check
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest

run-smoke:
	$(PYTHON) -m pytest tests/test_smoke.py -q

run-pipeline:
	$(PYTHON) scripts/run_pipeline.py

app:
	$(PYTHON) -m streamlit run app/streamlit_app.py
