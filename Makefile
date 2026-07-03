.PHONY: help dev rebuild deploy down logs test

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

dev: ## Start full stack locally (foreground)
	docker compose up

rebuild: ## Rebuild and restart after code changes (foreground, logs attached)
	docker compose up --build

deploy: ## Pull latest and rebuild on the server
	git pull && sudo docker compose up --build -d

down: ## Stop all containers
	sudo docker compose down

logs: ## Tail logs from all services
	sudo docker compose logs -f --tail=100

test: ## Run backend tests
	cd backend && python -m pytest
