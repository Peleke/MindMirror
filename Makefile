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

# Local Development (Docker Compose with local databases)
local:
	@echo "🚀 Starting MindMirror in LOCAL mode..."
	@echo "   - PostgreSQL: Local Docker container"
	@echo "   - Qdrant: Local Docker container"
	@echo "   - Redis: Local Docker container"
	@echo "   - GCS: Local emulator"
	ENV_FILE=env.local docker-compose up --build

# Staging Environment (Live databases, local services)
staging:
	@echo "🚀 Starting MindMirror in STAGING mode..."
	@echo "   - PostgreSQL: Live Supabase"
	@echo "   - Qdrant: Live Qdrant Cloud"
	@echo "   - Redis: Local Docker container"
	@echo "   - GCS: Live GCS bucket"
	ENV_FILE=env.staging docker-compose up --build

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
	@echo "  - Gateway: http://localhost:4000"
	@echo "  - Agent Service: http://localhost:8000"
	@echo "  - Journal Service: http://localhost:8001"
	@echo "  - Celery Worker: http://localhost:8002"
	@echo "  - Flower (Celery): http://localhost:5555"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Qdrant: http://localhost:6333"
	@echo "  - GCS Emulator: http://localhost:4443"

# GCS Configuration Commands
local-gcs-emulator:
	@echo "🔧 Switching to LOCAL GCS emulator..."
	@sed -i 's/USE_GCS_EMULATOR=false/USE_GCS_EMULATOR=true/' env.local
	@sed -i 's/STORAGE_EMULATOR_HOST=.*/STORAGE_EMULATOR_HOST=gcs-emulator:4443/' env.local
	@echo "✅ Switched to GCS emulator. Restart services with: make local"

local-gcs-real:
	@echo "🔧 Switching to REAL GCS (requires credentials)..."
	@echo "⚠️  Make sure you have:"
	@echo "   1. GCS service account credentials in ./credentials/"
	@echo "   2. Updated GCS_BUCKET_NAME in env.local"
	@echo "   3. Set GOOGLE_CLOUD_PROJECT in env.local"
	@sed -i 's/USE_GCS_EMULATOR=true/USE_GCS_EMULATOR=false/' env.local
	@sed -i 's/STORAGE_EMULATOR_HOST=.*/STORAGE_EMULATOR_HOST=/' env.local
	@echo "✅ Switched to real GCS. Restart services with: make local"

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