# ==========================================
# InnovateX Makefile
# ==========================================

.PHONY: help build up down restart logs clean dev prod test migrate

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(GREEN)InnovateX Docker Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Development environment started!$(NC)"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "PgAdmin: http://localhost:5050 (run 'make pgadmin' to start)"

dev-build: ## Build and start development environment
	@echo "$(GREEN)Building and starting development environment...$(NC)"
	docker-compose up -d --build
	@echo "$(GREEN)✅ Development environment built and started!$(NC)"

pgadmin: ## Start PgAdmin for database management
	@echo "$(GREEN)Starting PgAdmin...$(NC)"
	docker-compose --profile tools up -d pgadmin
	@echo "$(GREEN)✅ PgAdmin started at http://localhost:5050$(NC)"
	@echo "Email: admin@innovatex.com"
	@echo "Password: admin"

##@ Production

prod: ## Start production environment
	@echo "$(GREEN)Starting production environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ .env file not found! Please create it from .env.example$(NC)"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production environment started!$(NC)"

prod-build: ## Build and start production environment
	@echo "$(GREEN)Building and starting production environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ .env file not found! Please create it from .env.example$(NC)"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "$(GREEN)✅ Production environment built and started!$(NC)"

##@ Docker Operations

build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build

up: ## Start containers
	@echo "$(GREEN)Starting containers...$(NC)"
	docker-compose up -d

down: ## Stop and remove containers
	@echo "$(YELLOW)Stopping containers...$(NC)"
	docker-compose down

down-prod: ## Stop production containers
	@echo "$(YELLOW)Stopping production containers...$(NC)"
	docker-compose -f docker-compose.prod.yml down

restart: ## Restart containers
	@echo "$(YELLOW)Restarting containers...$(NC)"
	docker-compose restart

logs: ## Show logs from all containers
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-db: ## Show database logs
	docker-compose logs -f postgres

##@ Database

db-shell: ## Connect to PostgreSQL shell
	@echo "$(GREEN)Connecting to database...$(NC)"
	docker-compose exec postgres psql -U postgres -d innovatex_db

db-backup: ## Backup database
	@echo "$(GREEN)Backing up database...$(NC)"
	@mkdir -p ./backups
	docker-compose exec -T postgres pg_dump -U postgres innovatex_db > ./backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backed up to ./backups/$(NC)"

db-restore: ## Restore database from latest backup
	@echo "$(YELLOW)Restoring database from latest backup...$(NC)"
	@LATEST=$$(ls -t ./backups/*.sql | head -1); \
	if [ -z "$$LATEST" ]; then \
		echo "$(RED)❌ No backup files found!$(NC)"; \
		exit 1; \
	fi; \
	echo "Restoring from $$LATEST"; \
	docker-compose exec -T postgres psql -U postgres -d innovatex_db < $$LATEST
	@echo "$(GREEN)✅ Database restored!$(NC)"

##@ Testing & Monitoring

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	docker-compose exec backend pytest

shell: ## Open bash shell in backend container
	docker-compose exec backend /bin/bash

ps: ## Show running containers
	docker-compose ps

stats: ## Show container stats
	docker stats $$(docker-compose ps -q)

##@ Cleanup

clean: ## Remove containers, volumes, and orphans
	@echo "$(RED)Removing containers, volumes, and orphans...$(NC)"
	docker-compose down -v --remove-orphans
	@echo "$(GREEN)✅ Cleaned up!$(NC)"

clean-all: ## Remove everything including images
	@echo "$(RED)Removing everything...$(NC)"
	docker-compose down -v --rmi all --remove-orphans
	@echo "$(GREEN)✅ Everything cleaned up!$(NC)"

prune: ## Remove unused Docker resources
	@echo "$(YELLOW)Pruning unused Docker resources...$(NC)"
	docker system prune -af --volumes
	@echo "$(GREEN)✅ Docker pruned!$(NC)"

##@ Utilities

env: ## Create .env file from .env.example
	@if [ -f .env ]; then \
		echo "$(YELLOW)⚠️  .env file already exists!$(NC)"; \
	else \
		cp .env.example .env; \
		echo "$(GREEN)✅ .env file created from .env.example$(NC)"; \
		echo "$(YELLOW)⚠️  Please edit .env and update the values!$(NC)"; \
	fi

check: ## Check if Docker and Docker Compose are installed
	@echo "$(GREEN)Checking dependencies...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)❌ Docker is not installed$(NC)"; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "$(RED)❌ Docker Compose is not installed$(NC)"; exit 1; }
	@echo "$(GREEN)✅ Docker: $$(docker --version)$(NC)"
	@echo "$(GREEN)✅ Docker Compose: $$(docker-compose --version)$(NC)"

status: ## Show status of all services
	@echo "$(GREEN)Service Status:$(NC)"
	@docker-compose ps
