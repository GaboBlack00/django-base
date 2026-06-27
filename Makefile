.PHONY: help up down test lint format precommit migrate shell superuser bash logs

DC = docker compose
EXEC = $(DC) exec api

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	$(DC) up -d

down: ## Stop all services
	$(DC) down

test: ## Run tests with coverage
	$(EXEC) pytest --cov=. --cov-report=term-missing

lint: ## Run ruff linter (requires local ruff install)
	ruff check apps/ config/ tests/ conftest.py

format: ## Run ruff formatter (requires local ruff install)
	ruff format apps/ config/ tests/ conftest.py

precommit: ## Run pre-commit on all files
	pre-commit run --all-files

precommit-install: ## Install pre-commit hooks
	pre-commit install

migrate: ## Apply database migrations
	$(EXEC) python manage.py migrate

makemigrations: ## Create new migrations
	$(EXEC) python manage.py makemigrations

shell: ## Open Django shell
	$(EXEC) python manage.py shell

superuser: ## Create a superuser
	$(EXEC) python manage.py createsuperuser

bash: ## Open a shell inside the api container
	$(EXEC) bash

logs: ## Tail logs
	$(DC) logs -f
