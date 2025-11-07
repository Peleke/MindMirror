# =============================================================================
# MindMirror Development & Deployment Makefile
# =============================================================================

.PHONY: help local staging production clean logs

# Default target
help:
	@echo "MindMirror Development & Deployment Commands"
	@echo "============================================="
	@echo ""
	@echo "Environment Commands:"
	@echo "  make local      - Start with local environment (Docker Compose)"
	@echo "  make staging    - Start with staging environment (Live DBs)"
	@echo "  make production - Start with production environment"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean      - Stop and remove all containers"
	@echo "  make logs       - Show logs from all services"
	@echo "  make build      - Build all services"
	@echo "  make down       - Stop all services"
	@echo ""

# Local Development (Docker Compose with local databases + real Supabase auth)
local:
	@echo "🚀 Starting MindMirror in LOCAL mode..."
	@echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "   📦 Databases: Local Docker containers"
	@echo "      - PostgreSQL: postgres:5432"
	@echo "      - Qdrant: qdrant:6333"
	@echo "      - Redis: redis:6379"
	@echo "      - GCS: gcs-emulator:4443"
	@echo ""
	@echo "   🔐 Authentication: LIVE Supabase"
	@echo "      - Gateway JWT validation enabled"
	@echo "      - Web/Mobile Supabase auth enabled"
	@echo ""
	@echo "   🌐 Service URLs: Local Docker networking"
	@echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	ENV_FILE=.env.local docker-compose up -d --build

# Staging Environment (Live external services + local Redis)
staging:
	@echo "🚀 Starting MindMirror in STAGING mode..."
	@echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "   📦 Databases: Live External Services"
	@echo "      - PostgreSQL: Supabase (live)"
	@echo "      - Qdrant: Qdrant Cloud (live)"
	@echo "      - Redis: Local Docker container"
	@echo "      - GCS: Configurable (emulator or live)"
	@echo ""
	@echo "   🔐 Authentication: LIVE Supabase"
	@echo "      - Gateway JWT validation enabled"
	@echo "      - Web/Mobile Supabase auth enabled"
	@echo ""
	@echo "   🌐 Service URLs: Local Docker → will point to staging URLs"
	@echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	ENV_FILE=.env.staging docker-compose up -d --build

# Production Environment (Live everything)
production:
	@echo "🚀 Starting MindMirror in PRODUCTION mode..."
	@echo "   - PostgreSQL: Live Supabase"
	@echo "   - Qdrant: Live Qdrant Cloud"
	@echo "   - Redis: Live Redis Cloud"
	@echo "   - GCS: Live GCS bucket"
	ENV_FILE=env.production docker-compose up --build

# Build all services
build:
	@echo "🔨 Building all services..."
	docker-compose build

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose down

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Show logs
logs:
	@echo "📋 Showing logs..."
	docker-compose logs -f

# Health check
health:
	@echo "🏥 Checking service health..."
	docker-compose ps
	@echo ""
	@echo "Service URLs:"
	@echo "  - Web UI: http://localhost:3001"
	@echo "  - Mobile: Expo on http://localhost:8081"
	@echo "  - Gateway: http://localhost:4000/graphql"
	@echo "  - Agent Service: http://localhost:8000"
	@echo "  - Journal Service: http://localhost:8001"
	@echo "  - Habits Service: http://localhost:8003"
	@echo "  - Meals Service: http://localhost:8004"
	@echo "  - Movements Service: http://localhost:8005"
	@echo "  - Practices Service: http://localhost:8006"
	@echo "  - Users Service: http://localhost:8007"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Qdrant: http://localhost:6333"

# CLI Commands
cli-local:
	@echo "🔧 Running CLI in LOCAL mode..."
	cd cli && poetry run mindmirror qdrant health --env local

cli-staging:
	@echo "🔧 Running CLI in STAGING mode..."
	cd cli && poetry run mindmirror qdrant health --env live

# Database Commands
db-migrate-local:
	@echo "🗄️ Running migrations in LOCAL mode..."
	cd cli && poetry run mindmirror supabase upgrade --env local

db-migrate-staging:
	@echo "🗄️ Running migrations in STAGING mode..."
	cd cli && poetry run mindmirror supabase upgrade --env supabase

# Qdrant Commands
qdrant-seed-local:
	@echo "🌱 Seeding Qdrant in LOCAL mode..."
	cd cli && poetry run mindmirror qdrant build --env local

qdrant-seed-staging:
	@echo "🌱 Seeding Qdrant in STAGING mode..."
	cd cli && poetry run mindmirror qdrant seed --env live 