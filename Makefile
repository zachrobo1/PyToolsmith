.PHONY: reformat, setup-deps, setup-test, test

reformat:
	uv run ruff check --fix .

setup-deps:
	uv sync --frozen

setup-test:
	uv run pip install -e .

test:
	uv run pytest tests