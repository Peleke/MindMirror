# MindMirror Development Commands

.PHONY: demo clean logs help

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
	@echo ""
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Creating from template..."; \
		cp env.example .env; \
		echo "✅ .env file created. Please edit it to add your OpenAI API key or configure Ollama."; \
		echo ""; \
	fi
	@echo "🐳 Starting Docker containers..."
	docker-compose up --build -d
	@echo ""
	@echo "✅ MindMirror is starting up!"
	@echo "🔍 Monitor startup progress with: make logs"
	@echo "🚀 When ready, visit: http://localhost:3001"

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
	@echo ""
	@echo "Quick Access:"
	@echo "  make playground  Show GraphQL endpoint URLs"
	@echo ""
	@echo "URLs after 'make demo':"
	@echo "  📱 Web App:      http://localhost:3001 ✨ PRIMARY"
	@echo "  🎯 Streamlit:    http://localhost:8501 [Legacy]"
	@echo "  🌐 Gateway:      http://localhost:4000/graphql"
	@echo "  📊 Monitoring:   http://localhost:5555" 