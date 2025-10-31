# Tech Stack

**Document:** Architecture Shard - Technology Stack
**Version:** v4.0
**Last Updated:** 2025-10-15

---

## Existing Technology Stack

| Category | Current Technology | Version | Usage in Enhancement | Notes |
|----------|-------------------|---------|---------------------|-------|
| **Backend Framework** | FastAPI | Latest | No changes | All 7 microservices use FastAPI |
| **Backend Language** | Python | 3.11+ | No changes | Async/await with SQLAlchemy |
| **API Gateway** | GraphQL Hive Gateway | Latest | Rebuild supergraph | Federates microservice schemas |
| **GraphQL Client** | Apollo Client | 3.13.8 | Extend queries | Mobile + web apps |
| **Mobile Framework** | React Native (Expo) | 53.0.22 | Workout UI refactor | Expo Router navigation |
| **Mobile Language** | TypeScript | 5.8.3 | Workout component development | fp-ts functional programming |
| **Mobile UI Library** | Gluestack UI | 1.1.73 | Component redesign | Pre-built accessible components |
| **Web Framework** | Next.js | 15.3.3 | Admin UI extensions | App Router pattern |
| **Web UI Library** | Tailwind CSS | 4.1.10 | Admin dashboard styling | Utility-first CSS |
| **Authentication** | Supabase Auth | 2.50.0 | Production project setup | JWT + magic links |
| **Database (Main)** | PostgreSQL | 15 | No changes | Agent, Journal, Habits |
| **Database (Services)** | PostgreSQL | 15 | No changes | Movements, Practices, Users |
| **Vector Database** | Qdrant | Latest | No changes | RAG for journals |
| **Cache/Queue** | Redis | 7 | No changes | Celery task queue |
| **Background Workers** | Celery | Latest | No changes | Journal indexing |
| **ORM** | SQLAlchemy | Latest (async) | No changes | Repository pattern |
| **Migrations** | Alembic | Latest | No changes (validate schemas) | Each service isolated |
| **Container Orchestration** | Docker Compose | Latest | Local/staging only | Not used in production |
| **Cloud Platform** | Google Cloud Run | v1 (staging) | **Migrate to v2** | Production deployment |
| **IaC** | Terraform | Latest | **Refactor modules** | Cloud Run v2 migration |
| **Storage** | GCS (Emulator local) | N/A | No changes | Prompt storage factory |
| **Testing (Mobile)** | Jest + React Native Testing Library | 29.6.3 | **Add E2E tests** | Detox or Maestro TBD |
| **Testing (Backend)** | pytest | Latest | No changes | Existing unit tests |
| **Linting (Mobile)** | ESLint + TypeScript | 8.57.1 | No changes | Expo lint config |
| **Linting (Backend)** | Ruff/Black | N/A | No changes | Python formatting |

---

## New Technology Additions

| Technology | Version | Purpose | Rationale | Integration Method |
|-----------|---------|---------|-----------|-------------------|
| **Detox or Maestro** | Latest | React Native E2E testing | Automated regression tests for workout flow | Install via npm, integrate with Jest |
| **GCP Error Reporting SDK** | Latest | Mobile app error tracking | Lightweight alternative to Sentry for alpha | Install via npm, configure in app entry point |
| **Google Secret Manager** | N/A (GCP service) | Production secrets management | Secure API keys/credentials in Cloud Run | Mount secrets as volumes in Terraform |
| **Cloud Run v2** | N/A (Terraform module) | Modern serverless deployment | Improved cold starts, min instances, better logging | Replace `google_cloud_run_service` with `google_cloud_run_v2_service` |

---

## Service Architecture

### Backend Services (FastAPI/Python)

1. **Agent Service** (Port 8000) - AI conversation engine with LangGraph, RAG via Qdrant
2. **Journal Service** (Port 8001) - Structured journaling with automatic vector indexing
3. **Habits Service** (Port 8003) - Habit tracking and streaks
4. **Meals Service** (Port 8004) - Meal logging with Open Food Facts integration
5. **Movements Service** (Port 8005) - Exercise tracking with ExerciseDB API
6. **Practices Service** (Port 8006) - Meditation and mindfulness practices (workout programs)
7. **Users Service** (Port 8007) - User profiles and preferences

### Frontend Applications

- **Mobile App** (`mindmirror-mobile/`) - React Native with Expo, TypeScript + fp-ts, Apollo Client
- **Web App** (`web/`) - Next.js 15.3, Apollo Client, Supabase Auth, admin UI

### Infrastructure Services

- **GraphQL Gateway** (Port 4000) - Hive Gateway federating all microservice schemas
- **Celery Workers** - Background processing for journal indexing and document ingestion
- **Flower** (Port 5555) - Celery task monitoring UI

---

## Database Architecture

### PostgreSQL Databases

- **Main DB** (Port 5432): Agent, Journal, Habits services
- **Movements DB** (Port 5435): Movements service (isolated)
- **Practices DB** (Port 5436): Practices service (isolated)
- **Users DB** (Port 5437): Users service (isolated)

### Vector Database

- **Qdrant** (Port 6333/6334): Semantic search over journals and knowledge bases, organized by "traditions"

### Cache/Queue

- **Redis** (Port 6379): Celery task queue and caching

---

## External APIs

### ExerciseDB API
- **Purpose:** Exercise GIF demos and metadata
- **Base URL:** https://v2.exercisedb.io
- **Authentication:** API key
- **Integration:** Proxied through movements_service GraphQL

### Open Food Facts API
- **Purpose:** Nutrition data for meal logging
- **Integration:** Direct HTTP calls from meals_service

### Supabase
- **Purpose:** Authentication, user management, voucher storage
- **Integration:** SDK in mobile app, Admin SDK in web app

---

## Development Tools

- **Local Development:** Docker Compose, `make demo` command
- **Code Quality:** ESLint, Ruff, Black, TypeScript compiler
- **Testing:** pytest, Jest, React Native Testing Library
- **Version Control:** Git
- **CI/CD:** GitHub Actions (planned)
- **Monitoring:** Flower (Celery), GCP Logging, GCP Error Reporting
