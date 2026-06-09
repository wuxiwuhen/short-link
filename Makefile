.PHONY: install dev test lint format build run clean

# Install dependencies
install:
	pip install -r requirements.txt

# Install + watch mode
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests with coverage
test:
	pytest tests/ -v --cov=app --cov-report=term-missing

# Lint check
lint:
	ruff check app/ tests/
	ruff format --check app/ tests/

# Auto-fix lint issues
format:
	ruff check --fix app/ tests/
	ruff format app/ tests/

# Security audit
audit:
	pip-audit -r requirements.txt

# Docker build
build:
	docker build -t short-link:latest .

# Docker run
run: build
	docker compose up -d

# Stop containers
stop:
	docker compose down

# Clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
