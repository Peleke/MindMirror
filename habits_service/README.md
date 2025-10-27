# Habits Service

FastAPI + Strawberry GraphQL microservice for Habits, Lessons, and daily Tasks.

- Tech: FastAPI, Strawberry GraphQL, SQLAlchemy (async), asyncpg, Alembic
- Domain: Habit/Lesson/Program templates, step sequencing, daily task planning, user events (habit yes/no, lesson opened/completed), journal-as-habit card
- Endpoints:
  - GET /health → 200 OK for health checks
  - POST /graphql → GraphQL API (queries and mutations)

## Local Development

Prereqs: Docker, Docker Compose

Start the full stack (Postgres, Redis, gateway, etc.)

```bash
docker compose up -d postgres redis qdrant
docker compose up -d agent_service journal_service habits_service
docker compose up -d mesh-compose gateway
```

Service URLs (by default):

- Habits Service: http://localhost:8003
- GraphQL (via Gateway): http://localhost:4000/graphql

The service will ensure schema `habits` exists and create tables on startup for local dev.

## Seeding Content (Lessons/Programs)

Use the CLI container to seed the 7-habit program and lessons either locally or to Supabase.

Local database (Compose Postgres):

```bash
docker compose run --rm \
  -e DATABASE_SCHEMA=habits \
  cli mindmirror seed-habits run
```

Supabase (live):

```bash
docker compose run --rm \
  -e CLI_ENV=live \
  -e SUPABASE_DATABASE_URL="$SUPABASE_DATABASE_URL" \
  -e DATABASE_SCHEMA=habits \
  cli mindmirror seed-habits run --env live
```

Note: On first run against Supabase, add missing columns once via SQL:

```sql
ALTER TABLE habits.program_templates
  ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1,
  ADD COLUMN IF NOT EXISTS content_hash varchar,
  ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;

ALTER TABLE habits.lesson_templates
  ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1,
  ADD COLUMN IF NOT EXISTS content_hash varchar,
  ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true,
  ADD COLUMN IF NOT EXISTS metadata_json jsonb;
```

## GraphQL

Example query (via gateway /graphql):

```graphql
query TodaysTasks($date: String!) {
  todaysTasks(onDate: $date) {
    __typename
    ... on HabitTask { taskId title description status habitTemplateId }
    ... on LessonTask { taskId title summary status lessonTemplateId }
    ... on JournalTask { taskId title description status }
  }
}
```

Key queries (subset): `todaysTasks`, `programTemplates`, `programTemplateBySlug`, `programAssignments`.

Key mutations (subset): record habit/lesson/journal events; CRUD for templates and structural entities.

## Running Tests

Build with dev deps (default in compose):

```bash
docker compose build habits_service
```

Run tests inside the service container:

```bash
docker compose run --rm habits_service bash -lc "pytest -q"
```

Integration tests use a throwaway schema per test and auto-create tables.

## Alembic (optional for local)

Make targets are provided for convenience:

```bash
cd habits_service
make alembic.init   # initialize if needed
make alembic.rev m="your message"  # create revision (autogenerate)
make alembic.up     # upgrade to head
```

For local dev we also create tables on app startup; use Alembic for snapshots/staging.

## Cloud Run Deployment

Images are built via GitHub Actions workflow `.github/workflows/local.yaml`.

To build locally with `act` and get a push command:

```bash
act workflow_dispatch -W .github/workflows/local.yaml -j build --input service=habits_service
```

Deploy with Terraform/Tofu using `infra/modules/habits_service` and set the image to the built tag. Outputs include the service URL.

## Troubleshooting

- asyncpg build issues: Use Python 3.11; `asyncpg` pinned to `^0.30.0`.
- Missing columns on Supabase: run the ALTERs above once.
- Compose healthchecks: ensure `habits_service` exposes `/health` and is referenced by mesh-compose before composing the supergraph.


