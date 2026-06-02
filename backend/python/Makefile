.PHONY: help install dev test lint format migrate migrate-create run docker-build docker-up docker-down clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest tests/ $(ARGS)

test-unit: ## Run unit tests only
	pytest tests/ -m unit $(ARGS)

test-integration: ## Run integration tests only
	pytest tests/ -m integration $(ARGS)

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/
	isort src/ tests/

typecheck: ## Run type checking
	mypy src/

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-shell: ## Open shell in app container
	docker-compose exec app bash

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create a new migration
	@read -p "Migration name: " name; alembic revision --autogenerate -m "$$name"

migrate-rollback: ## Rollback last migration
	alembic downgrade -1

db-shell: ## Open database shell
	docker-compose exec db psql -U postgres -d psd_dev

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

clean: ## Clean up cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

celery-worker: ## Start Celery worker
	celery -A src.workers.celery_app worker --loglevel=info

celery-beat: ## Start Celery beat scheduler
	celery -A src.workers.celery_app beat --loglevel=info

celery-flower: ## Start Celery Flower monitoring
	celery -A src.workers.celery_app flower

requirements: ## Generate requirements.txt from pyproject.toml
	pip-compile pyproject.toml --output-file requirements.txt

requirements-dev: ## Generate requirements-dev.txt
	pip-compile pyproject.toml --dev --output-file requirements-dev.txt
