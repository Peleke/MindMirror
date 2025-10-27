# Source Tree

**Document:** Architecture Shard - Source Tree Organization
**Version:** v4.0
**Last Updated:** 2025-10-15

---

## Complete Project Structure

```
MindMirror/
├── .bmad-core/                     # BMAD agent framework
│   ├── agents/                     # Agent personas (architect, pm, dev, qa)
│   ├── tasks/                      # Executable workflows
│   ├── templates/                  # Document templates
│   ├── checklists/                 # Validation checklists
│   └── data/                       # Elicitation methods, technical preferences
│
├── src/                            # Backend microservices (shared infra)
│   ├── agent_service/              # AI conversation + RAG engine
│   │   ├── app/
│   │   │   ├── main.py             # FastAPI entry point
│   │   │   ├── config.py           # Environment configuration
│   │   │   ├── api/                # REST + GraphQL routers
│   │   │   ├── clients/            # External service clients
│   │   │   ├── services/           # Business logic (LLM, Qdrant, traditions)
│   │   │   ├── repositories/       # Data access (GCS, traditions)
│   │   │   └── graphql/            # GraphQL schema + resolvers
│   │   ├── langgraph_/             # LangGraph orchestration
│   │   │   ├── graphs/             # Chat, journal, review graphs
│   │   │   └── nodes/              # Graph nodes (summarizer, reviewer)
│   │   ├── llms/                   # LLM providers (OpenAI, Gemini, Ollama)
│   │   │   ├── providers/          # Provider implementations
│   │   │   └── prompts/            # Prompt storage (YAML/GCS/Memory)
│   │   ├── mcp/                    # Model Context Protocol
│   │   │   ├── tools/              # MCP tool definitions
│   │   │   └── retrievers/         # Journal retriever
│   │   ├── tests/                  # Unit tests
│   │   └── Dockerfile              # Container image
│   │
│   ├── journal_service/            # Structured journaling
│   │   ├── journal_service/
│   │   │   ├── main.py             # FastAPI entry point
│   │   │   ├── app/
│   │   │   │   ├── db/             # Database repositories
│   │   │   │   │   └── repositories/
│   │   │   │   └── graphql/        # GraphQL schema
│   │   │   └── models/             # Pydantic + SQLAlchemy models
│   │   ├── tests/
│   │   └── Dockerfile
│   │
│   ├── alembic-config/             # Database migrations (Agent, Journal, Habits)
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/               # Migration scripts
│   │
│   └── shared/                     # Shared utilities
│       └── auth.py                 # Supabase JWT authentication
│
├── habits_service/                 # Habit tracking (independent DB)
│   ├── habits_service/
│   │   └── app/
│   │       ├── main.py
│   │       ├── db/                 # Database repositories
│   │       ├── graphql/            # GraphQL schema
│   │       └── models/             # SQLAlchemy models
│   ├── alembic/                    # Habits DB migrations
│   ├── tests/
│   └── Dockerfile
│
├── meals_service/                  # Meal logging (independent service)
│   ├── meals_service/
│   │   ├── main.py
│   │   ├── db/
│   │   ├── graphql/
│   │   └── models/
│   ├── tests/
│   └── Dockerfile
│
├── movements_service/              # Exercise tracking (independent DB)
│   ├── movements_service/
│   │   ├── main.py
│   │   ├── db/
│   │   ├── graphql/
│   │   ├── models/
│   │   └── clients/
│   │       └── exercisedb.py       # ExerciseDB API client
│   ├── alembic/                    # Movements DB migrations
│   ├── tests/
│   └── Dockerfile
│
├── practices_service/              # Workout programs (independent DB)
│   ├── practices/
│   │   ├── main.py
│   │   ├── repository/
│   │   │   ├── models/
│   │   │   │   └── practice_instance.py  # Contains notes, duration fields
│   │   │   └── enrollment_resolvers.py   # autoEnrollPractices mutation
│   │   ├── graphql/
│   │   └── db/
│   ├── alembic/                    # Practices DB migrations
│   ├── tests/
│   └── Dockerfile
│
├── users_service/                  # User profiles (independent DB)
│   ├── users_service/
│   │   ├── main.py
│   │   ├── db/
│   │   ├── graphql/
│   │   └── models/
│   ├── alembic/                    # Users DB migrations
│   ├── tests/
│   └── Dockerfile
│
├── celery-worker/                  # Background tasks
│   ├── src/
│   │   └── tasks/                  # Celery task definitions
│   │       ├── index_journal_task.py
│   │       └── build_knowledge_base.py
│   ├── start.sh                    # Worker startup script
│   └── Dockerfile
│
├── web/                            # Next.js admin + landing page
│   ├── app/                        # Next.js App Router
│   │   ├── page.tsx                # Landing page
│   │   ├── layout.tsx              # Root layout
│   │   ├── (auth)/                 # Auth routes
│   │   ├── admin/                  # Admin dashboard
│   │   │   ├── vouchers/           # **NEW: Magic link generator**
│   │   │   │   └── create/
│   │   │   │       └── page.tsx
│   │   │   ├── programs/           # **NEW: Program dashboard**
│   │   │   │   └── page.tsx
│   │   │   └── analytics/          # **NEW: Activity monitoring**
│   │   │       └── page.tsx
│   │   └── api/                    # API routes
│   │       ├── health/
│   │       └── vouchers/           # Voucher creation endpoint
│   │           └── create/
│   │               └── route.ts    # **EXTENDED: Magic link generation**
│   ├── lib/                        # Utilities
│   │   ├── apollo/                 # Apollo Client setup
│   │   └── supabase/               # Supabase client + Admin SDK
│   ├── components/                 # Shared components
│   ├── public/                     # Static assets
│   ├── package.json
│   └── next.config.js
│
├── mindmirror-mobile/              # React Native mobile app
│   ├── app/                        # Expo Router routes
│   │   ├── _layout.tsx             # Root layout
│   │   ├── index.tsx               # Entry screen
│   │   ├── (auth)/                 # Auth screens
│   │   │   ├── login.tsx
│   │   │   └── signup.tsx
│   │   └── (app)/                  # Main app screens
│   │       ├── _layout.tsx         # Tab navigator
│   │       ├── dashboard/
│   │       ├── journal/
│   │       ├── chat/
│   │       └── client/
│   │           └── [id].tsx        # Workout screen (to be refactored)
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/             # Shared components
│   │   │   └── ui/                 # Gluestack UI wrappers
│   │   ├── features/               # Feature-specific components
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── journal/
│   │   │   ├── chat/
│   │   │   └── practices/          # **NEW: Workout components**
│   │   │       └── components/
│   │   │           ├── ExerciseCard.tsx         # **NEW**
│   │   │           ├── SetTable.tsx             # **NEW**
│   │   │           ├── RestTimerModal.tsx       # **NEW**
│   │   │           └── CircularProgressRing.tsx # **NEW**
│   │   ├── lib/                    # Utilities
│   │   │   ├── apollo/             # Apollo Client setup
│   │   │   └── supabase/           # Supabase Auth
│   │   └── graphql/                # GraphQL queries/mutations
│   ├── __tests__/                  # Tests
│   │   ├── auth.test.tsx
│   │   └── e2e/                    # **NEW: E2E tests**
│   │       └── workout-flow.spec.ts
│   ├── package.json
│   └── app.json                    # Expo configuration
│
├── mesh/                           # GraphQL Hive Gateway
│   ├── gateway.config.ts           # Gateway configuration
│   ├── mesh.config.dynamic.ts      # Service URLs configuration
│   ├── mesh.config.ts              # Mesh composition config
│   ├── build/                      # Generated supergraph
│   │   └── supergraph.graphql
│   ├── Dockerfile
│   └── Dockerfile.mesh-compose
│
├── infra/                          # Terraform infrastructure
│   ├── main.tf                     # Root module
│   ├── versions.tf
│   ├── providers.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── base/                       # Base infrastructure (GCS, secrets)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── envs/
│   │   ├── staging/
│   │   │   └── backend.tf          # Terraform state backend
│   │   └── prod/
│   │       └── backend.tf
│   └── modules/                    # Service modules
│       ├── agent_service/
│       │   ├── main.tf             # **MODIFIED: Cloud Run v2**
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── journal_service/
│       │   └── main.tf             # **MODIFIED: Cloud Run v2**
│       ├── habits_service/
│       │   └── main.tf             # **MODIFIED: Cloud Run v2**
│       ├── meals/
│       │   └── main.tf             # **MODIFIED: Cloud Run v2**
│       ├── movements/
│       │   └── main.tf             # **MODIFIED: Cloud Run v2**
│       ├── practices/
│       │   └── main.tf             # **MODIFIED: Cloud Run v2**
│       ├── users/
│       │   └── main.tf             # **MODIFIED: Cloud Run v2**
│       ├── gateway/
│       │   └── main.tf             # **MODIFIED: Cloud Run v2**
│       └── celery-worker/
│           └── main.tf             # **MODIFIED: Cloud Run v2**
│
├── cli/                            # MindMirror CLI tool
│   ├── src/
│   │   └── mindmirror/
│   │       ├── cli.py              # CLI entry point
│   │       ├── commands/           # CLI commands (qdrant, supabase)
│   │       └── utils/
│   ├── pyproject.toml
│   └── README.md
│
├── docs/                           # Project documentation
│   ├── architecture.md             # **NEW: This architecture document**
│   ├── architecture/               # **NEW: Architecture shards**
│   │   ├── tech-stack.md
│   │   ├── coding-standards.md
│   │   └── source-tree.md
│   ├── prd.md                      # Product Requirements Document (v4)
│   ├── brief.md                    # Project brief
│   ├── alpha-validation-week-1.md
│   ├── week-1-execution-checklist.md
│   ├── design-system.md
│   ├── component-specs.md
│   ├── front-end-spec.md
│   ├── epics/
│   │   ├── epic-1-admin-tooling.md
│   │   ├── epic-2-workout-ui-ux.md
│   │   ├── epic-3-infrastructure.md
│   │   └── epic-4-testing-framework.md
│   ├── stories/                    # User stories
│   │   ├── 1.1-magic-link-ui.md
│   │   ├── 1.2-program-dashboard.md
│   │   ├── 2.1-exercise-card-redesign.md
│   │   └── ... (14 total stories)
│   ├── testing/                    # **NEW: Testing documentation**
│   │   ├── voucher-flow-test-script.md
│   │   └── bug-triage-process.md
│   └── prd/                        # Sharded PRD (if sharded)
│
├── local_gcs_bucket/               # Local GCS emulator storage
│   └── {tradition}/
│       └── documents/              # Knowledge base documents
│
├── .env                            # Local environment variables
├── env.staging                     # Staging environment variables
├── env.production                  # Production environment variables
├── docker-compose.yml              # Docker Compose orchestration
├── Makefile                        # Development commands
├── CLAUDE.md                       # Project instructions for AI agents
├── README.md                       # Project README
└── pyproject.toml                  # Root Python dependencies
```

---

## Service Port Mapping

| Service | Port | Description |
|---------|------|-------------|
| **web** | 3001 | Next.js admin/landing page |
| **gateway** | 4000 | GraphQL Hive Gateway |
| **agent_service** | 8000 | AI conversation + RAG |
| **journal_service** | 8001 | Journaling |
| **celery-worker-web** | 8002 | Celery worker HTTP endpoint |
| **habits_service** | 8003 | Habit tracking |
| **meals_service** | 8004 | Meal logging |
| **movements_service** | 8005 | Exercise tracking |
| **practices_service** | 8006 (mapped to 8000) | Workout programs |
| **users_service** | 8007 (mapped to 8000) | User profiles |
| **postgres** | 5432 | Main PostgreSQL (Agent, Journal, Habits) |
| **movements_postgres** | 5435 | Movements PostgreSQL |
| **practices_postgres** | 5436 | Practices PostgreSQL |
| **users_postgres** | 5437 | Users PostgreSQL |
| **redis** | 6379 | Redis cache/queue |
| **qdrant** | 6333 (HTTP), 6334 (gRPC) | Qdrant vector DB |
| **gcs-emulator** | 4443 | GCS emulator |
| **celery_flower** | 5555 | Flower task monitoring |

---

## Key File Locations

### Backend Entry Points

- **Agent Service:** `src/agent_service/app/main.py`
- **Journal Service:** `src/journal_service/journal_service/main.py`
- **Habits Service:** `habits_service/habits_service/app/main.py`
- **Meals Service:** `meals_service/meals_service/main.py`
- **Movements Service:** `movements_service/movements_service/main.py`
- **Practices Service:** `practices_service/practices/main.py`
- **Users Service:** `users_service/users_service/main.py`

### Frontend Entry Points

- **Web App:** `web/app/page.tsx`
- **Mobile App:** `mindmirror-mobile/app/_layout.tsx`

### Infrastructure

- **GraphQL Gateway:** `mesh/gateway.config.ts`
- **Docker Compose:** `docker-compose.yml`
- **Terraform Root:** `infra/main.tf`
- **Makefile:** `Makefile`

### Important Utilities

- **Shared Auth:** `src/shared/auth.py`
- **Storage Factory:** `src/agent_service/app/services/prompt_service_factory.py`
- **CLI Entry:** `cli/src/mindmirror/cli.py`
- **Celery Tasks:** `celery-worker/src/tasks/`

---

## Enhancement File Additions

### New Files

```
web/src/app/admin/
├── vouchers/create/page.tsx        # Magic link generator
├── programs/page.tsx               # Program dashboard
└── analytics/page.tsx              # Activity monitoring

mindmirror-mobile/src/features/practices/components/
├── ExerciseCard.tsx                # Exercise card redesign
├── SetTable.tsx                    # Set logging table
├── RestTimerModal.tsx              # Rest timer modal
└── CircularProgressRing.tsx        # Progress indicator

mindmirror-mobile/__tests__/e2e/
└── workout-flow.spec.ts            # E2E test suite

docs/
├── architecture.md                 # This architecture document
├── architecture/
│   ├── tech-stack.md
│   ├── coding-standards.md
│   └── source-tree.md
└── testing/
    ├── voucher-flow-test-script.md
    └── bug-triage-process.md
```

### Modified Files

```
infra/modules/*/main.tf             # Cloud Run v2 migration (all services)
web/src/app/api/vouchers/create/route.ts  # Extended voucher endpoint
```

---

## Import/Export Patterns

### Python Services

```python
# Absolute imports from root
from agent_service.app.services import LLMService
from journal_service.models.pydantic import JournalEntry
from shared.auth import get_current_user

# Relative imports within service
from .repository import UserRepository
from ..models import User
```

### TypeScript (Mobile)

```typescript
// Absolute imports via module resolver
import { Button } from '@/components/ui/button';
import { useWorkout } from '@/features/practices/hooks';

// Barrel exports
// src/components/ui/index.ts
export * from './button';
export * from './card';
export * from './input';

// Usage
import { Button, Card, Input } from '@/components/ui';
```

### TypeScript (Web)

```typescript
// Next.js absolute imports
import { createClient } from '@/lib/supabase/server';
import { ProgramDashboard } from '@/components/admin/ProgramDashboard';

// Relative imports
import { MagicLinkForm } from './MagicLinkForm';
import type { Program } from '../types';
```

---

## Configuration Files

### Root Configuration

- **Docker Compose:** `docker-compose.yml` - Service orchestration
- **Makefile:** `Makefile` - Development commands (local, staging, production)
- **Python Dependencies:** `pyproject.toml` - Root Python packages
- **BMAD Config:** `.bmad-core/core-config.yaml` - Agent framework configuration

### Backend Services

- **Python Package:** `pyproject.toml` per service (agent, journal, habits, etc.)
- **Database Migrations:** `alembic.ini` per service
- **Environment Variables:** `.env`, `env.staging`, `env.production`

### Frontend Applications

- **Mobile:** `mindmirror-mobile/package.json`, `app.json` (Expo config)
- **Web:** `web/package.json`, `next.config.js`
- **Gateway:** `mesh/gateway.config.ts`, `mesh.config.dynamic.ts`

### Infrastructure

- **Terraform:** `infra/versions.tf`, `infra/providers.tf`
- **Backend:** `infra/envs/staging/backend.tf`, `infra/envs/prod/backend.tf`

---

## Data Storage Locations

### Databases

- **PostgreSQL (Main):** Container volume `postgres_data`
- **PostgreSQL (Movements):** Container volume `movements_postgres_data`
- **PostgreSQL (Practices):** Container volume `practices_postgres_data`
- **PostgreSQL (Users):** Container volume `users_postgres_data`
- **Qdrant:** Container volume `qdrant_data`

### Files

- **Prompts (Local):** `local_gcs_bucket/` (GCS emulator)
- **Prompts (Production):** GCS bucket `mindmirror-prompts`
- **Knowledge Base Documents:** `local_gcs_bucket/{tradition}/documents/`

---

## Testing Structure

### Backend (pytest)

```
src/agent_service/
├── app/
│   └── services/
│       └── llm_service.py
└── tests/
    └── services/
        └── test_llm_service.py
```

### Frontend (Jest)

```
mindmirror-mobile/
├── src/features/practices/
│   └── components/
│       └── ExerciseCard.tsx
└── __tests__/
    ├── features/practices/
    │   └── ExerciseCard.test.tsx
    └── e2e/
        └── workout-flow.spec.ts
```

---

## Environment Variables

### Location

- **Local:** `.env` (default)
- **Staging:** `env.staging`
- **Production:** `env.production`
- **Service-Specific:** Passed via `docker-compose.yml` environment section

### Critical Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# External Services
QDRANT_URL=http://qdrant:6333
REDIS_URL=redis://redis:6379/0
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_JWT_SECRET=xxx

# Storage
PROMPT_STORAGE_TYPE=gcs|yaml|memory
GCS_BUCKET_NAME=mindmirror-prompts
GCS_EMULATOR_HOST=gcs-emulator:4443

# APIs
OPENAI_API_KEY=sk-xxx
EXERCISEDB_API_KEY=xxx
```
