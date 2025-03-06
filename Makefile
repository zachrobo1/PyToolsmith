.PHONY: reformat, setup-deps, setup-test, test, test-with-coverage

reformat:
	uv run ruff check --fix .

setup-deps:
	uv sync --frozen

setup-test:
	uv sync --dev && uv pip install -e .

test:
	uv run pytest tests/

test-in-ci:
	uv run pytest --cov=src/pytoolsmith --cov-report=xml:coverage.xml --cov-report=term -k "not llm_test" tests/