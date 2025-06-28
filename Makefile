# MindMirror Development Commands

.PHONY: demo clean logs help init-storage health-check

# Default target
.DEFAULT_GOAL := help

# Demo environment - launches the full stack
demo:
	@echo "🚀 Launching MindMirror Demo Environment..."
	@echo "📋 This will start all services:"
	@echo "   - Next.js Web App (http://localhost:3001) ✨ PRIMARY INTERFACE"
	@echo "   - Streamlit UI (http://localhost:8501) [Legacy]"  
	@echo "   - GraphQL Gateway (http://localhost:4000/graphql)"
	@echo "   - Task Monitoring (http://localhost:5555)"
	@echo "   - GCS Emulator (http://localhost:4443)"
	@echo ""
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Creating from template..."; \
		cp env.example .env; \
		echo "✅ .env file created. Please edit it to add your OpenAI API key or configure Ollama."; \
		echo ""; \
	fi
	@echo "📁 Creating necessary directories..."
	@mkdir -p prompts credentials local_gcs_bucket
	@echo "🔧 Installing MindMirror CLI..."
	@if [ -f cli/pyproject.toml ]; then \
		cd cli && poetry install; \
	fi
	@echo "🧠 Building knowledge base..."
	@make build-knowledge-base
	@echo "🐳 Starting Docker containers..."
	docker-compose up --build -d
	@echo ""
	@echo "⏳ Waiting for services to start..."
	@sleep 10
	@echo "🔧 Initializing storage..."
	@make init-storage
	@echo ""
	@echo "✅ MindMirror is starting up!"
	@echo "🔍 Monitor startup progress with: make logs"
	@echo "🏥 Check health with: make health-check"
	@echo "🚀 When ready, visit: http://localhost:3001"

# Build knowledge base
build-knowledge-base:
	@echo "🧠 Building Qdrant knowledge base..."
	@if [ -f cli/pyproject.toml ]; then \
		echo "📚 Running MindMirror CLI..."; \
		cd cli && poetry run mindmirror qdrant build --tradition canon-default --verbose || echo "⚠️  Knowledge base build failed or skipped"; \
	else \
		echo "⚠️  MindMirror CLI not found, falling back to script..."; \
		poetry run python scripts/build_qdrant_knowledge_base.py || echo "⚠️  Knowledge base build failed or skipped"; \
	fi
	@echo "✅ Knowledge base build complete!"

# Initialize storage (GCS bucket, prompts directory)
init-storage:
	@echo "🔧 Initializing storage..."
	@if [ -f scripts/init-gcs-bucket.sh ]; then \
		echo "📦 Setting up GCS bucket..."; \
		docker-compose exec -T gcs-emulator sh -c "sleep 5" 2>/dev/null || true; \
		./scripts/init-gcs-bucket.sh 2>/dev/null || echo "⚠️  GCS initialization skipped (emulator may not be ready)"; \
	else \
		echo "📁 Creating prompts directory..."; \
		mkdir -p prompts; \
	fi
	@echo "✅ Storage initialization complete!"

# Health check for all services
health-check:
	@echo "🏥 Running health checks..."
	@if [ -f scripts/health-check.sh ]; then \
		./scripts/health-check.sh; \
	else \
		echo "📊 Checking service status..."; \
		docker-compose ps; \
		echo ""; \
		echo "🔍 Manual health checks:"; \
		echo "  - Web App: curl http://localhost:3001/api/health"; \
		echo "  - Agent Service: curl http://localhost:8000/health"; \
		echo "  - Gateway: curl http://localhost:4000/healthcheck"; \
	fi

# Stop all services
stop:
	@echo "🛑 Stopping MindMirror services..."
	docker-compose down

# View logs from all services
logs:
	@echo "📋 Showing logs from all services (Ctrl+C to exit)..."
	docker-compose logs -f

# Clean up everything (containers, volumes, networks)
clean:
	@echo "🧹 Cleaning up MindMirror environment..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup complete!"

# Show service status
status:
	@echo "📊 MindMirror Service Status:"
	docker-compose ps

# Rebuild and restart a specific service
rebuild:
	@if [ -z "$(service)" ]; then \
		echo "❌ Please specify a service: make rebuild service=<service_name>"; \
		echo "Available services: web, agent_service, journal_service, ui, gateway"; \
	else \
		echo "🔄 Rebuilding $(service)..."; \
		docker-compose up --build -d $(service); \
	fi

# Open GraphQL playground
playground:
	@echo "🎮 Opening GraphQL Playground..."
	@echo "Gateway: http://localhost:4000/graphql"
	@echo "Agent Service: http://localhost:8000/graphql"
	@echo "Journal Service: http://localhost:8001/graphql"

# Run tests
test:
	@echo "🧪 Running tests..."
	docker-compose exec agent_service pytest
	docker-compose exec journal_service pytest

# Switch storage backend
switch-storage:
	@if [ -z "$(type)" ]; then \
		echo "❌ Please specify storage type: make switch-storage type=<yaml|gcs|memory>"; \
		echo "Available types: yaml, gcs, memory"; \
	else \
		echo "🔄 Switching to $(type) storage..."; \
		export PROMPT_STORAGE_TYPE=$(type); \
		docker-compose up -d agent_service celery_worker; \
		echo "✅ Switched to $(type) storage"; \
	fi

# Show help
help:
	@echo "🧠 MindMirror Development Commands"
	@echo ""
	@echo "Main Commands:"
	@echo "  make demo        Launch the full MindMirror stack"
	@echo "  make stop        Stop all running services"
	@echo "  make clean       Stop and remove all containers/volumes"
	@echo ""
	@echo "Development:"
	@echo "  make logs        View logs from all services"
	@echo "  make status      Show current service status"
	@echo "  make rebuild service=<name>  Rebuild specific service"
	@echo "  make test        Run test suites"
	@echo "  make health-check Check health of all services"
	@echo ""
	@echo "Storage Management:"
	@echo "  make init-storage Initialize storage (GCS bucket, prompts)"
	@echo "  make switch-storage type=<yaml|gcs|memory>  Switch storage backend"
	@echo "  make build-knowledge-base Build Qdrant knowledge base"
	@echo ""
	@echo "Quick Access:"
	@echo "  make playground  Show GraphQL endpoint URLs"
	@echo ""
	@echo "URLs after 'make demo':"
	@echo "  📱 Web App:      http://localhost:3001 ✨ PRIMARY"
	@echo "  🎯 Streamlit:    http://localhost:8501 [Legacy]"
	@echo "  🌐 Gateway:      http://localhost:4000/graphql"
	@echo "  📊 Monitoring:   http://localhost:5555"
	@echo "  ☁️  GCS Emulator: http://localhost:4443" 