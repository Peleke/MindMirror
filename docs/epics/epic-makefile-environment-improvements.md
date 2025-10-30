# Epic: Makefile Environment Improvements

**Epic ID**: `epic-makefile-environment-improvements`
**Status**: 🔄 In Progress
**Priority**: HIGH
**Target Completion**: 2025-10-29 (Today)
**Owner**: DevOps/Infrastructure
**Effort**: 2 hours

---

## Problem Statement

The current Makefile supports `make local`, `make staging`, and `make production`, but:

1. **Authentication Gap**: Local and staging modes use local databases but need real Supabase authentication for the gateway, web, and mobile apps to function properly
2. **Inconsistent Configuration**: No clear separation between service-to-service communication (local Docker networking) and client authentication (Supabase JWT)
3. **Testing Limitations**: Cannot properly test `/sdl` endpoints and gateway federation locally with real auth

**Impact**: Developers cannot fully test authentication flows locally, staging testing requires manual environment switching, gateway development is painful.

---

## Solution Overview

Update `make local` and `make staging` to:
- Use **local Docker databases** for backend services (PostgreSQL, Qdrant, Redis, GCS emulator)
- Inject **real Supabase variables** for authentication (gateway, web, mobile)
- Support `/sdl` endpoint testing without authentication
- Maintain service-to-service communication via Docker networking (no auth yet)

This enables:
- ✅ Full-stack local development with real authentication
- ✅ Gateway JWT validation testing locally
- ✅ Staging mode that mirrors production architecture
- ✅ Easy switching between environments

---

## Stories

### Story 1: Update `make local` for Real Supabase Auth
**Status**: ✅ Complete
**Priority**: HIGH
**Effort**: 1 hour

**Goal**: Enable local development with Docker databases + real Supabase authentication.

**Tasks**:
- [x] Create `.env.local` file with Supabase variables
- [x] Update `Makefile` to use `ENV_FILE=.env.local`
- [x] Update `docker-compose.yml` to inject Supabase variables for gateway/web/mobile
- [x] Keep local Docker containers for PostgreSQL, Qdrant, Redis, GCS emulator
- [ ] Verify gateway can validate Supabase JWT locally (needs testing)
- [ ] Test end-to-end: Login → GraphQL query with JWT (needs testing)

**Environment Variables (`.env.local`)**:
```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Local Development with Real Supabase Auth
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Supabase Authentication (Real)
NEXT_PUBLIC_SUPABASE_URL=https://gaitofyakycvpwqfoevq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
SUPABASE_JWT_SECRET=<jwt_secret>

# Local Databases (Docker)
DATABASE_URL=postgresql+asyncpg://mindmirror:mindmirror@postgres:5432/mindmirror_db
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379

# GCS Emulator (Local)
PROMPT_STORAGE_TYPE=gcs
GCS_EMULATOR_HOST=gcs-emulator:4443
GCS_BUCKET_NAME=local_gcs_bucket
GOOGLE_CLOUD_PROJECT=mindmirror-local

# Gateway Configuration (Local services)
JOURNAL_SERVICE_URL=http://journal_service:8001
AGENT_SERVICE_URL=http://agent_service:8000
HABITS_SERVICE_URL=http://habits_service:8003
MEALS_SERVICE_URL=http://meals_service:8004
MOVEMENTS_SERVICE_URL=http://movements_service:8005
PRACTICES_SERVICE_URL=http://practices_service:8000
USERS_SERVICE_URL=http://users_service:8000

# Other
OPENAI_API_KEY=<your_key>
LOG_LEVEL=DEBUG
DEBUG=true
```

**Acceptance Criteria**:
- ✅ `make local` starts all services with local DBs
- ✅ Gateway validates Supabase JWT tokens
- ✅ Web app can authenticate users
- ✅ Mobile app can authenticate users
- ✅ Services respond to `/sdl` without auth
- ✅ GraphQL queries require JWT auth

**Files Modified**:
- `Makefile`
- `docker-compose.yml` (environment variable mappings)

**Files Created**:
- `.env.local`

---

### Story 2: Update `make staging` for Live External Services
**Status**: ⏳ Not Started
**Priority**: HIGH
**Effort**: 1 hour

**Goal**: Enable staging mode that connects to live Supabase, Qdrant, and optionally GCS.

**Tasks**:
- [ ] Update `.env.staging` with Supabase variables
- [ ] Update `.env.staging` with live Qdrant Cloud URL
- [ ] Update `Makefile` to use `ENV_FILE=.env.staging`
- [ ] Update `docker-compose.yml` to support conditional GCS emulator
- [ ] Keep Redis local (Docker container)
- [ ] Test connection to live databases
- [ ] Verify gateway can reach live services

**Environment Variables (`.env.staging`)**:
```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Staging Environment - Live External Services
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Supabase (Live)
NEXT_PUBLIC_SUPABASE_URL=https://gaitofyakycvpwqfoevq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
SUPABASE_JWT_SECRET=<jwt_secret>

# Database (Live Supabase PostgreSQL)
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@db.<project>.supabase.co:5432/postgres

# Qdrant (Live Cloud)
QDRANT_URL=https://<cluster>.qdrant.io
QDRANT_API_KEY=<api_key>

# Redis (Local Docker)
REDIS_URL=redis://redis:6379

# GCS (Live or Emulator - Configurable)
PROMPT_STORAGE_TYPE=gcs
GCS_BUCKET_NAME=traditions-mindmirror-69
GOOGLE_CLOUD_PROJECT=mindmirror-69
# GCS_EMULATOR_HOST=gcs-emulator:4443  # Uncomment for emulator

# Gateway (Local services pointing to staging URLs - will be updated)
JOURNAL_SERVICE_URL=http://journal_service:8001
AGENT_SERVICE_URL=http://agent_service:8000
# ... (will be updated to point to staging Cloud Run URLs for testing)

# Other
OPENAI_API_KEY=<your_key>
LOG_LEVEL=INFO
DEBUG=false
```

**Acceptance Criteria**:
- ✅ `make staging` connects to live Supabase PostgreSQL
- ✅ Services connect to live Qdrant Cloud
- ✅ Gateway validates JWTs against live Supabase
- ✅ Can optionally use GCS emulator or live GCS
- ✅ Redis runs locally (Docker)
- ✅ All services start successfully

**Files Modified**:
- `Makefile`
- `.env.staging`
- `docker-compose.yml` (conditional GCS configuration)

---

## Makefile Changes

### Current Implementation
```makefile
local:
	@echo "🚀 Starting MindMirror in LOCAL mode..."
	ENV_FILE=env.local docker-compose up --build

staging:
	@echo "🚀 Starting MindMirror in STAGING mode..."
	ENV_FILE=env.staging docker-compose up --build
```

### Updated Implementation
```makefile
local:
	@echo "🚀 Starting MindMirror in LOCAL mode..."
	@echo "   - PostgreSQL: Local Docker container"
	@echo "   - Qdrant: Local Docker container"
	@echo "   - Redis: Local Docker container"
	@echo "   - GCS: Local emulator"
	@echo "   - Supabase Auth: LIVE (gateway/web/mobile)"
	ENV_FILE=.env.local docker-compose up --build

staging:
	@echo "🚀 Starting MindMirror in STAGING mode..."
	@echo "   - PostgreSQL: Live Supabase"
	@echo "   - Qdrant: Live Qdrant Cloud"
	@echo "   - Redis: Local Docker container"
	@echo "   - GCS: Configurable (emulator or live)"
	@echo "   - Supabase Auth: LIVE"
	ENV_FILE=.env.staging docker-compose up --build
```

---

## Docker Compose Changes

### Gateway Service Environment Variables

**Current** (incomplete):
```yaml
gateway:
  env_file: ${ENV_FILE:-.env}
  environment:
    - NODE_ENV=development
```

**Updated** (with Supabase):
```yaml
gateway:
  env_file: ${ENV_FILE:-.env}
  environment:
    - NODE_ENV=development
    - SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}
    - JOURNAL_SERVICE_URL=${JOURNAL_SERVICE_URL:-http://journal_service:8001}
    - AGENT_SERVICE_URL=${AGENT_SERVICE_URL:-http://agent_service:8000}
    - HABITS_SERVICE_URL=${HABITS_SERVICE_URL:-http://habits_service:8003}
    - MEALS_SERVICE_URL=${MEALS_SERVICE_URL:-http://meals_service:8004}
    - MOVEMENTS_SERVICE_URL=${MOVEMENTS_SERVICE_URL:-http://movements_service:8005}
    - PRACTICES_SERVICE_URL=${PRACTICES_SERVICE_URL:-http://practices_service:8000}
    - USERS_SERVICE_URL=${USERS_SERVICE_URL:-http://users_service:8000}
```

### Web Service Environment Variables

**Current** (incomplete):
```yaml
web:
  env_file: ${ENV_FILE:-.env}
  environment:
    - NODE_ENV=development
    - NEXT_PUBLIC_GATEWAY_URL=http://gateway:4000/graphql
```

**Updated** (with Supabase):
```yaml
web:
  env_file: ${ENV_FILE:-.env}
  environment:
    - NODE_ENV=development
    - NEXT_PUBLIC_GATEWAY_URL=http://gateway:4000/graphql
    - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
    - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
    - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

---

## Testing Checklist

### Local Mode (`make local`)
- [ ] All services start without errors
- [ ] PostgreSQL accessible on `localhost:5432`
- [ ] Qdrant accessible on `localhost:6333`
- [ ] Redis accessible on `localhost:6379`
- [ ] GCS emulator accessible on `localhost:4443`
- [ ] Gateway health check: `curl http://localhost:4000/healthcheck`
- [ ] Services respond to `/sdl`: `curl http://localhost:8000/sdl` (agent)
- [ ] Web app loads: `http://localhost:3001`
- [ ] Can authenticate via Supabase in web app
- [ ] GraphQL query with JWT succeeds: `curl -H "Authorization: Bearer <token>" http://localhost:4000/graphql`
- [ ] GraphQL query without JWT fails with 401

### Staging Mode (`make staging`)
- [ ] All services start without errors
- [ ] Services connect to live Supabase PostgreSQL
- [ ] Services connect to live Qdrant Cloud
- [ ] Redis runs locally
- [ ] GCS configuration works (emulator or live)
- [ ] Gateway validates JWTs against live Supabase
- [ ] Can authenticate via Supabase
- [ ] GraphQL queries work with JWT

---

## Success Metrics

1. **Local Development**: Developers can run full stack locally with real auth
2. **Iteration Speed**: < 30 seconds from code change to test
3. **Staging Parity**: Staging mode accurately mirrors production architecture
4. **Authentication**: 100% JWT validation success rate locally
5. **Zero Friction**: One command to start each environment

---

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Project overview
- [Epic: Gateway Rebuild Automation](./epic-gateway-rebuild-automation.md) - Related workflow improvements

---

**Last Updated**: 2025-10-29
**Status**: 🔄 In Progress - Story 1 Active
