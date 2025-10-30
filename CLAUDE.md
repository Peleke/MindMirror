# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MindMirror is an AI-powered personal performance platform built with a federated microservices architecture. The system combines journal entries and curated knowledge bases using RAG (Retrieval-Augmented Generation) to provide personalized coaching.

**Key Architecture Pattern:** Federated GraphQL microservices orchestrated through GraphQL Hive gateway, with real-time background processing via Celery workers.

## Development Environment Setup

### Quick Start
```bash
# Launch full stack with Docker Compose
make demo

# Access services:
# - Web UI: http://localhost:3001
# - Mobile: cd mindmirror-mobile && npm start
# - GraphQL Gateway: http://localhost:4000/graphql
# - Flower (task monitoring): http://localhost:5555
```

### Environment Switching
The project supports multiple deployment environments through the `ENV_FILE` variable:
```bash
make local      # Local Docker databases (default .env)
make staging    # Live Supabase + Qdrant Cloud (env.staging)
make production # Full production (env.production)
```

### Storage Backend Configuration
MindMirror uses a factory pattern for configurable storage backends:
- **YAML Storage** (development): Local YAML files in `./prompts`
- **GCS Storage** (production): Google Cloud Storage bucket
- **Memory Storage** (fallback): In-memory store for testing
- **GCS Emulator** (local testing): Local GCS emulation via `fake-gcs-server`

Storage type is automatically selected based on `PROMPT_STORAGE_TYPE` environment variable or environment defaults. See `src/agent_service/app/services/prompt_service_factory.py` for implementation.

## Service Architecture

### Core Services (Python/FastAPI)

#### 1. Agent Service (Port 8000)
Location: `src/agent_service/`
- AI conversation engine with LangGraph orchestration
- RAG implementation using Qdrant vector database
- Knowledge base management and document ingestion
- Configurable storage backend (YAML/GCS/Memory)
- **Start:** `poetry run uvicorn agent_service.app.main:app --reload --port 8000`

#### 2. Journal Service (Port 8001)
Location: `src/journal_service/`
- Manages structured journaling (gratitude, reflection, freeform)
- Automatic indexing to Qdrant via Celery tasks
- Repository pattern with SQLAlchemy async
- **Start:** `poetry run uvicorn journal_service.journal_service.main:app --reload --port 8001`

#### 3. Habits Service (Port 8003)
Location: `habits_service/`
- Habit tracking and streaks
- Independent database (schema: `habits`)
- **Start:** `poetry run uvicorn habits_service.habits_service.app.main:app --reload --port 8003`

#### 4. Meals Service (Port 8004)
Location: `meals_service/`
- Meal logging and nutrition tracking
- Integration with Open Food Facts API
- **Start:** From service directory

#### 5. Movements Service (Port 8005)
Location: `movements_service/`
- Exercise and workout tracking
- Separate PostgreSQL database (`swae_movements`)
- ExerciseDB API integration
- **Start:** From service directory

#### 6. Practices Service (Port 8006)
Location: `practices_service/`
- Meditation and mindfulness practices
- Separate PostgreSQL database (`swae_practices`)
- **Start:** From service directory

#### 7. Users Service (Port 8007)
Location: `users_service/`
- User profile and preferences
- Separate PostgreSQL database (`swae_users`)
- **Start:** From service directory

### Background Workers

#### Celery Worker
Location: `celery-worker/`
- Indexes journal entries into Qdrant for semantic search
- Processes document uploads for knowledge base
- Shares storage configuration with Agent Service
- **Monitoring:** Flower UI at http://localhost:5555

**Critical Pattern:** Journal entries trigger `index_journal_task` which runs asynchronously to update the vector database. The worker uses the same storage factory pattern as Agent Service.

### Frontend Applications

#### Next.js Web App (Port 3001)
Location: `web/`
- Landing page and web interface
- Apollo Client for GraphQL communication
- Supabase authentication
- **Deployment modes:**
  - `NEXT_PUBLIC_APP_MODE=demo`: Full features (local)
  - Default: Landing page only (production)
- **Dev:** `cd web && npm run dev`
- **Build:** `cd web && npm run build`

#### React Native Mobile App (Expo)
Location: `mindmirror-mobile/`
- TypeScript with functional programming (fp-ts)
- Apollo Client + Supabase Auth
- Expo Router for navigation
- **Dev:** `npm start` then press `i` (iOS) or `a` (Android)
- **Test:** `npm test`
- **Type Check:** `npm run type-check`
- **Lint:** `npm run lint:fix`

### API Gateway

#### GraphQL Hive Gateway (Port 4000)
Location: `mesh/`
- Federates all microservice GraphQL schemas
- JWT authentication via custom directives
- Two-stage build process:
  1. `mesh-compose`: Composes supergraph from services
  2. `gateway`: Serves federated schema
- **Config:** `mesh/gateway.config.ts` and `mesh/mesh.config.ts`
- Services must be healthy before composition runs

## Database Architecture

### PostgreSQL Databases
- **Main DB** (Port 5432): Agent, Journal, Habits services
- **Movements DB** (Port 5435): Movements service only
- **Practices DB** (Port 5436): Practices service only
- **Users DB** (Port 5437): Users service only

### Migrations
- **Agent/Journal:** Alembic migrations in `src/alembic-config/`
- **Habits:** Alembic in `habits_service/alembic/`
- **Movements:** Alembic in `movements_service/alembic/`
- **Practices:** Alembic in `practices_service/alembic/`

Run migrations:
```bash
# From CLI
cd cli && poetry run mindmirror supabase upgrade --env local

# Or directly with Alembic
cd src/alembic-config && alembic upgrade head
```

### Vector Database (Qdrant)
- **Port:** 6333 (HTTP), 6334 (gRPC)
- Collections organized by "traditions" (knowledge domains)
- Used for semantic search over journals and knowledge bases

## CLI Tool

Location: `cli/`

The MindMirror CLI manages knowledge bases and system health checks:

```bash
cd cli && poetry install

# Check Qdrant health
poetry run mindmirror qdrant health

# Build knowledge base
poetry run mindmirror qdrant build --tradition canon-default --verbose

# List traditions
poetry run mindmirror qdrant list-traditions

# Database migrations
poetry run mindmirror supabase upgrade --env local
```

## Testing

### Python Services
```bash
# From project root
poetry run pytest

# Specific service
cd src/agent_service && poetry run pytest

# With coverage
poetry run pytest --cov=agent_service
```

### Mobile App
```bash
cd mindmirror-mobile
npm test              # Run all tests
npm run test:watch    # Watch mode
npm run test:coverage # With coverage
```

### Web App
```bash
cd web
npm test
```

## Common Development Tasks

### Building Knowledge Base
```bash
# Using CLI (recommended)
cd cli && poetry run mindmirror qdrant build --tradition canon-default --verbose

# Using legacy script
poetry run python scripts/build_qdrant_knowledge_base.py
```

Knowledge bases are built from documents in:
- `local_gcs_bucket/{tradition}/documents/` (modern)
- `pdfs/{tradition}/` (legacy)

### Switching Storage Backends
```bash
# Switch to GCS emulator (local development)
export PROMPT_STORAGE_TYPE=gcs
export GCS_EMULATOR_HOST=gcs-emulator:4443
export GCS_BUCKET_NAME=local_gcs_bucket

# Switch to real GCS (staging/production)
export PROMPT_STORAGE_TYPE=gcs
export GCS_BUCKET_NAME=mindmirror-prompts
export GCS_CREDENTIALS_FILE=/path/to/credentials.json

# Switch to YAML (simple local dev)
export PROMPT_STORAGE_TYPE=yaml
export YAML_STORAGE_PATH=./prompts
```

### Working with GraphQL Gateway
After modifying a service's GraphQL schema:
1. Ensure service is running and healthy
2. Gateway will auto-rebuild on startup via `mesh-compose` service
3. Test at http://localhost:4000/graphql

### Viewing Celery Tasks
- Navigate to http://localhost:5555 (Flower)
- Monitor task execution, failures, and queue status

### Service Health Checks
```bash
# All services
curl http://localhost:8000/health  # Agent
curl http://localhost:8001/health  # Journal
curl http://localhost:8003/health  # Habits
curl http://localhost:8004/health  # Meals
curl http://localhost:8005/health  # Movements
curl http://localhost:8006/health  # Practices (mapped to 8000 internally)
curl http://localhost:8007/health  # Users (mapped to 8000 internally)
curl http://localhost:4000/healthcheck  # Gateway
```

## Key Implementation Patterns

### 1. Storage Factory Pattern
See `src/agent_service/app/services/prompt_service_factory.py`:
- Environment-based storage selection
- Graceful fallback to memory storage
- Shared between Agent Service and Celery Workers

### 2. Repository Pattern
Services use repository pattern for data access:
- `src/journal_service/journal_service/app/db/repositories/`
- SQLAlchemy with async/await
- Clean separation of data access from business logic

### 3. Service Communication
- **Synchronous:** Direct HTTP calls for immediate data (e.g., Journal Service → Agent Service)
- **Asynchronous:** Celery tasks for background processing (e.g., indexing)
- **GraphQL:** Client-facing queries/mutations through federated gateway

### 4. Authentication Flow
1. Supabase handles user authentication (web/mobile)
2. JWT tokens passed to gateway
3. Gateway validates and extracts user context
4. Services receive authenticated user via dependency injection
5. Example: `shared.auth.get_current_user()` dependency

### 5. Document Tradition Organization
Knowledge bases are organized by "traditions" (philosophical/domain frameworks):
- Each tradition has a collection in Qdrant
- Documents stored in `{storage_backend}/{tradition}/documents/`
- Traditions discovered dynamically from storage backend
- Configurable via `TRADITION_DISCOVERY_MODE` env var

## Infrastructure Commands

```bash
# Start everything
make demo

# View logs
make logs

# Stop services
make down

# Clean everything (remove volumes)
make clean

# Health check
make health

# Rebuild specific service
docker-compose up -d --build agent_service
```

## Python Package Management

Project uses **Poetry** for Python dependency management:
- Root `pyproject.toml`: Shared dependencies for agent/journal services
- Individual service `pyproject.toml` files for isolated services
- **Important:** Run `poetry install` from appropriate directory before development

## TypeScript/JavaScript Package Management

- **Web:** `npm` (Next.js)
- **Mobile:** `npm` (Expo/React Native)
- **Gateway:** `npm` (GraphQL Hive)

## Environment Variables

Critical environment variables (see `.env` file):

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

### Storage
- `PROMPT_STORAGE_TYPE`: `yaml|gcs|memory`
- `GCS_BUCKET_NAME`: GCS bucket name
- `GCS_EMULATOR_HOST`: Local GCS emulator (dev only)
- `YAML_STORAGE_PATH`: Local YAML storage path

### External Services
- `QDRANT_URL`: Qdrant vector database URL
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: OpenAI API key for embeddings/LLM
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

### Application
- `NEXT_PUBLIC_APP_MODE`: `demo` (full features) or production (landing only)
- `TRADITION_DISCOVERY_MODE`: `gcs-first|local-first|hybrid`

## Troubleshooting

### Gateway won't start
- Ensure all microservices are healthy (`make health`)
- Check `mesh-compose` service logs for schema composition errors
- Verify service URLs in `mesh/mesh.config.dynamic.ts`

### Celery tasks not running
- Check Redis connection
- Verify Celery worker is running (`docker ps | grep celery`)
- View Flower UI for task failures

### Knowledge base queries return no results
- Verify Qdrant has collections: `cd cli && poetry run mindmirror qdrant list-collections`
- Rebuild knowledge base: `poetry run mindmirror qdrant build`
- Check tradition name matches collection name

### Storage backend issues
- Verify `PROMPT_STORAGE_TYPE` environment variable
- For GCS emulator: ensure `gcs-emulator` container is running
- For real GCS: verify credentials and bucket access
- Check logs for storage factory fallback messages

### Database connection errors
- Verify PostgreSQL container is running
- Check `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/db`
- For separate service DBs, check corresponding DB environment variables

## Architecture Decisions

### Why Federated GraphQL?
- Independent service development and deployment
- Type-safe API composition
- Single entry point for frontend clients
- Each service owns its domain schema

### Why Separate Databases for Some Services?
- Movements, Practices, and Users services have independent databases
- Allows for future service extraction and scaling
- Clear data ownership boundaries
- Main DB still shared by Agent/Journal/Habits for historical reasons

### Why Celery for Background Tasks?
- Asynchronous indexing keeps API responses fast
- Retries and failure handling for external service calls
- Monitoring and observability via Flower
- Scalable: add more workers as needed

### Why Multiple Storage Backends?
- Development: YAML for simplicity and git-trackable prompts
- Production: GCS for scalability and reliability
- Testing: Memory for fast, isolated tests
- Environment parity: GCS emulator bridges local and production

## File Reference Quick Links

- **Agent Service Main:** `src/agent_service/app/main.py`
- **Journal Service Main:** `src/journal_service/journal_service/main.py`
- **Storage Factory:** `src/agent_service/app/services/prompt_service_factory.py`
- **GraphQL Gateway:** `mesh/gateway.config.ts`
- **Docker Compose:** `docker-compose.yml`
- **Celery Tasks:** `celery-worker/src/tasks/`
- **Mobile App Entry:** `mindmirror-mobile/app/(app)/_layout.tsx`
- **Web App Entry:** `web/app/page.tsx`
- **Shared Auth:** `src/shared/auth.py`
- **CLI Entry:** `cli/src/mindmirror/cli.py`
