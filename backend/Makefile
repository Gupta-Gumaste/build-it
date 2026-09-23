.PHONY: build run test

build:
	uv sync

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest
