.PHONY: install dev start test lint

install:
	uv pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start:
	uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

test:
	pytest

lint:
	ruff check .
	ruff fix . 