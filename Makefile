.PHONY: install run test test-cov help

help:
	@echo "Available commands:"
	@echo "  make install    Install all dependencies"
	@echo "  make run        Start the AI Study Assistant"
	@echo "  make test       Run the test suite"
	@echo "  make test-cov   Run tests with coverage report"

install:
	pip install -r requirements.txt

run:
	python main.py

test:
	pytest tests/

test-cov:
	pytest tests/ --cov=src --cov-report=term-missing
