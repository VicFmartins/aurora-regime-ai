PYTHON ?= python

.PHONY: install format lint test run-smoke app

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

format:
	ruff format .
	ruff check . --fix

lint:
	ruff format . --check
	ruff check .

test:
	pytest

run-smoke:
	pytest tests/test_smoke.py -q

app:
	streamlit run app/streamlit_app.py
