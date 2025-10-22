.PHONY: help install start stop restart logs logs-backend logs-postgres clean build rebuild shell-backend shell-postgres frontend test-backend test-frontend pgadmin status setup dev

# Colori per output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
NC     := \033[0m # No Color

help: ## Mostra questo messaggio di aiuto
	@echo "$(GREEN)Casa&Più - Comandi Disponibili$(NC)"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Installa dipendenze (frontend + backend)
	@echo "$(YELLOW)📦 Installando dipendenze frontend...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✅ Frontend pronto$(NC)"

start: ## Avvia lo stack completo con Docker Compose
	@echo "$(YELLOW)🚀 Avvio stack Casa&Più...$(NC)"
	@./start-local.sh

stop: ## Ferma lo stack
	@echo "$(YELLOW)🛑 Fermando stack...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✅ Stack fermato$(NC)"

restart: ## Riavvia lo stack
	@echo "$(YELLOW)🔄 Riavvio stack...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)✅ Stack riavviato$(NC)"

logs: ## Visualizza logs di tutti i servizi
	@docker-compose logs -f

logs-backend: ## Visualizza logs del backend
	@docker-compose logs -f backend

logs-postgres: ## Visualizza logs di PostgreSQL
	@docker-compose logs -f postgres

clean: ## Ferma e rimuove container, volumi e immagini
	@echo "$(YELLOW)🧹 Pulizia completa...$(NC)"
	@docker-compose down -v --remove-orphans
	@echo "$(GREEN)✅ Pulizia completata$(NC)"

build: ## Ricostruisci le immagini Docker
	@echo "$(YELLOW)🔨 Building immagini...$(NC)"
	@docker-compose build
	@echo "$(GREEN)✅ Build completato$(NC)"

rebuild: ## Ricostruisci e riavvia
	@$(MAKE) build
	@$(MAKE) start

shell-backend: ## Accedi alla shell del container backend
	@docker-compose exec backend bash

shell-postgres: ## Accedi a PostgreSQL
	@docker-compose exec postgres psql -U casapiu -d casapiu

frontend: ## Avvia il frontend in development
	@echo "$(YELLOW)🌐 Avvio frontend...$(NC)"
	@cd frontend && npm start

test-backend: ## Esegui test backend
	@echo "$(YELLOW)🧪 Esecuzione test backend...$(NC)"
	@cd backend && pytest

test-frontend: ## Esegui test frontend
	@echo "$(YELLOW)🧪 Esecuzione test frontend...$(NC)"
	@cd frontend && npm test

pgadmin: ## Avvia PgAdmin
	@echo "$(YELLOW)🔧 Avvio PgAdmin...$(NC)"
	@docker-compose --profile tools up -d pgadmin
	@echo "$(GREEN)✅ PgAdmin disponibile su http://localhost:5050$(NC)"
	@echo "   Email: admin@casapiu.local | Password: admin"

status: ## Mostra stato servizi
	@docker-compose ps

setup: install ## Setup completo progetto
	@echo "$(YELLOW)⚙️  Setup progetto...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(YELLOW)📝 File .env creato. Configura le credenziali!$(NC)"; \
	fi
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "$(YELLOW)📝 File backend/.env creato.$(NC)"; \
	fi
	@if [ ! -f frontend/.env ]; then \
		cp frontend/.env.example frontend/.env; \
		echo "$(YELLOW)📝 File frontend/.env creato.$(NC)"; \
	fi
	@echo "$(GREEN)✅ Setup completato!$(NC)"
	@echo "$(YELLOW)⚠️  Ricorda di configurare i file .env prima di avviare lo stack$(NC)"

dev: ## Avvia stack + frontend in modalità sviluppo
	@$(MAKE) start
	@sleep 5
	@$(MAKE) frontend
