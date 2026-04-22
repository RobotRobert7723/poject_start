.PHONY: install lint test

install:
	python -m pip install -e .[dev]

lint:
	ruff check src tests
	mypy src

test:
	pytest
