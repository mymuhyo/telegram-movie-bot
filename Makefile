.PHONY: install dev test lint format migrate run docker-up docker-down clean

# Installation
install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Testing
test:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

# Linting & Formatting
lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

# Database
migrate:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m "$(name)"

migrate-down:
	alembic downgrade -1

# Run
run:
	python -m src.bot.main

run-dev:
	DEBUG=true python -m src.bot.main

# Docker
docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down

docker-logs:
	docker compose -f docker/docker-compose.yml logs -f bot

docker-build:
	docker compose -f docker/docker-compose.yml build

# Utilities
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache

backup:
	python scripts/backup_db.py

create-admin:
	python scripts/create_admin.py $(id)
