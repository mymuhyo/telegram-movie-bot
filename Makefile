# =============================================================================
# Movie Bot Makefile
# =============================================================================
# Usage: make <target>
# =============================================================================

.PHONY: help install dev test lint format build up down logs shell migrate backup clean

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# Help
# =============================================================================
help: ## Show this help message
	@echo "Movie Bot - Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================
install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt 2>/dev/null || pip install pytest pytest-asyncio pytest-cov black ruff mypy

# =============================================================================
# Code Quality
# =============================================================================
lint: ## Run linter and type checker
	ruff check src/ tests/
	mypy src/

format: ## Format code with ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

# =============================================================================
# Testing
# =============================================================================
test: ## Run all tests
	pytest tests/ -v --cov=src --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-cov: ## Run tests with HTML coverage report
	pytest tests/ -v --cov=src --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# =============================================================================
# Database Migrations
# =============================================================================
migrate: ## Run database migrations
	alembic upgrade head

migrate-new: ## Create new migration (usage: make migrate-new name="migration name")
	alembic revision --autogenerate -m "$(name)"

migrate-down: ## Rollback last migration
	alembic downgrade -1

migrate-history: ## Show migration history
	alembic history

# =============================================================================
# Local Development
# =============================================================================
run: ## Run bot locally
	python -m src.bot.main

run-dev: ## Run bot in debug mode
	DEBUG=true python -m src.bot.main

# =============================================================================
# Docker Commands
# =============================================================================
build: ## Build Docker images
	docker compose -f docker/docker-compose.yml build

up: ## Start all services in background
	docker compose -f docker/docker-compose.yml up -d

up-dev: ## Start all services including dev tools (Adminer, Redis Commander)
	docker compose -f docker/docker-compose.yml --profile dev up -d

up-logs: ## Start all services with logs
	docker compose -f docker/docker-compose.yml up

down: ## Stop all services
	docker compose -f docker/docker-compose.yml down

restart: ## Restart bot service only
	docker compose -f docker/docker-compose.yml restart bot

logs: ## Show bot logs (follow mode)
	docker compose -f docker/docker-compose.yml logs -f bot

logs-all: ## Show all services logs
	docker compose -f docker/docker-compose.yml logs -f

shell: ## Open shell in bot container
	docker compose -f docker/docker-compose.yml exec bot bash

db-shell: ## Open PostgreSQL shell
	docker compose -f docker/docker-compose.yml exec postgres psql -U moviebot -d moviebot

redis-cli: ## Open Redis CLI
	docker compose -f docker/docker-compose.yml exec redis redis-cli

status: ## Show services status
	docker compose -f docker/docker-compose.yml ps

# =============================================================================
# Docker Migrations
# =============================================================================
docker-migrate: ## Run migrations in Docker
	docker compose -f docker/docker-compose.yml exec bot alembic upgrade head

docker-migrate-new: ## Create migration in Docker (usage: make docker-migrate-new name="msg")
	docker compose -f docker/docker-compose.yml exec bot alembic revision --autogenerate -m "$(name)"

# =============================================================================
# Backup & Restore
# =============================================================================
backup: ## Create database backup
	@mkdir -p backups/postgres
	docker compose -f docker/docker-compose.yml exec postgres pg_dump -U moviebot moviebot > backups/postgres/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created successfully"

restore: ## Restore from backup (usage: make restore FILE=path/to/backup.sql)
	@if [ -z "$(FILE)" ]; then echo "Usage: make restore FILE=path/to/backup.sql"; exit 1; fi
	docker compose -f docker/docker-compose.yml exec -T postgres psql -U moviebot moviebot < $(FILE)
	@echo "Backup restored successfully"

backup-local: ## Create local database backup
	python scripts/backup_db.py

# =============================================================================
# Utilities
# =============================================================================
clean: ## Clean Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

clean-docker: ## Clean Docker resources
	docker compose -f docker/docker-compose.yml down -v --remove-orphans
	docker system prune -f

clean-all: ## Clean everything including Docker volumes
	$(MAKE) clean
	docker compose -f docker/docker-compose.yml down -v --remove-orphans
	docker volume rm moviebot_postgres_data moviebot_redis_data 2>/dev/null || true

create-admin: ## Create admin user (usage: make create-admin id=123456789)
	python scripts/create_admin.py $(id)

health: ## Check services health
	@echo "Checking services..."
	@docker compose -f docker/docker-compose.yml exec postgres pg_isready -U moviebot && echo "PostgreSQL: OK" || echo "PostgreSQL: NOT READY"
	@docker compose -f docker/docker-compose.yml exec redis redis-cli ping | grep -q PONG && echo "Redis: OK" || echo "Redis: NOT READY"

# =============================================================================
# Production Deployment
# =============================================================================
deploy: ## Deploy to production (pull, build, migrate, restart)
	@echo "Deploying to production..."
	git pull origin main
	docker compose -f docker/docker-compose.yml build
	docker compose -f docker/docker-compose.yml up -d
	docker compose -f docker/docker-compose.yml exec bot alembic upgrade head
	@echo "Deployment complete!"

deploy-quick: ## Quick deploy (restart only, no rebuild)
	docker compose -f docker/docker-compose.yml restart bot
	@echo "Bot restarted!"
