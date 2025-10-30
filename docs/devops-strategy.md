# MindMirror DevOps Strategy
**Version**: 1.0
**Last Updated**: 2025-10-24
**Context**: Solo/small team, GCP-based, secure + streamlined + automated

---

## Executive Summary

This strategy establishes a **production-ready, automated deployment pipeline** for MindMirror's federated microservices architecture. Built for solo/small teams with GCP infrastructure, prioritizing security, simplicity, and automation over enterprise complexity.

**Key Principles**:
- ✅ Secure by default (Secret Manager, least privilege IAM)
- ✅ Automated where it counts (build, test, deploy)
- ✅ Streamlined for small teams (minimal ceremony, maximum value)
- ✅ Production-first with `infra-v2/` (OpenTofu)
- ✅ Staging follows later (proven pattern replication)

---

## Architecture Overview

### Deployment Environments

```
┌─────────────────────────────────────────────────────────────┐
│                      LOCAL DEVELOPMENT                       │
├─────────────────────────────────────────────────────────────┤
│  • Docker Compose (docker-compose.yml)                      │
│  • Local PostgreSQL databases                                │
│  • GCS Emulator (fake-gcs-server)                           │
│  • Environment: .env file                                    │
│  • Schema: Auto-created via metadata.create_all()           │
│  • Purpose: Development and testing                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              STAGING (Future - Post-Production)              │
├─────────────────────────────────────────────────────────────┤
│  • Infrastructure: infra-v2/ (duplicated from production)   │
│  • Cloud Run services (GCP)                                  │
│  • Cloud SQL (PostgreSQL)                                    │
│  • Qdrant Cloud                                              │
│  • GCS for storage                                           │
│  • Secret Manager for secrets                                │
│  • Schema: Alembic migrations                                │
│  • Purpose: Pre-production validation                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  PRODUCTION (Priority #1)                    │
├─────────────────────────────────────────────────────────────┤
│  • Infrastructure: infra-v2/ (OpenTofu)                     │
│  • Cloud Run Gen2 services (GCP)                             │
│  • Cloud SQL (PostgreSQL) - 4 instances                      │
│  • Qdrant Cloud (vector DB)                                  │
│  • GCS for document storage                                  │
│  • Secret Manager for all secrets                            │
│  • Secret volume mounts at /secrets/<volume>/<file>          │
│  • Schema: Alembic migrations only                           │
│  • Artifact Registry for container images                    │
│  • Cloud Logging + Error Reporting                           │
└─────────────────────────────────────────────────────────────┘
```

**Legacy (Manual Management)**:
- `infra/` - Terraform-based staging (hand-managed, keep for now)
- Live Supabase + Qdrant Cloud
- Accessed via `make staging` (uses `env.staging`)

---

## Container Registry & Image Management

### Strategy: Google Artifact Registry

**Why Artifact Registry?**
- Native GCP integration (IAM, Secret Manager, Cloud Run)
- Vulnerability scanning built-in
- Better pricing than GCR for small teams
- Docker-compatible

**Registry Structure**:
```
us-central1-docker.pkg.dev/mindmirror-prod/services/
├── agent-service:main-abc123
├── agent-service:v1.2.3
├── journal-service:main-abc123
├── habits-service:main-abc123
├── meals-service:main-abc123
├── movements-service:main-abc123
├── practices-service:main-abc123
├── users-service:main-abc123
├── celery-worker:main-abc123
├── mesh-gateway:main-abc123
└── web-app:main-abc123
```

**Image Tagging Strategy**:
1. **Git SHA tags** (primary): `main-abc123`, `staging-abc123`
   - Immutable, traceable to exact commit
   - Used for deployments
2. **Semantic version tags** (releases): `v1.2.3`, `v1.2.3-rc1`
   - For versioned releases
   - Optional, used when tagging releases
3. **Environment tags** (aliases): `production-latest`, `staging-latest`
   - Updated on successful deployments
   - For quick rollbacks

**Multi-Architecture**: Single arch (linux/amd64) to start, expand if needed

**Image Retention**:
- Keep last 10 images per service
- Delete untagged images after 30 days
- Never delete images with semantic version tags

**Vulnerability Scanning**:
- Automatic on push via Artifact Registry
- Block deployments with CRITICAL vulnerabilities
- Weekly scans of production images

---

## CI/CD Pipeline Architecture

### GitHub Actions Workflow Structure

```
.github/workflows/
├── ci-python-services.yml          # Shared Python service CI
├── ci-web.yml                       # Next.js web app CI
├── ci-mobile.yml                    # React Native mobile CI
├── cd-deploy-service.yml            # Reusable deployment workflow
├── build-and-push.yml               # Reusable Docker build/push
└── rollback.yml                     # Manual rollback workflow
```

### Trigger Strategy

**On Pull Request**:
- Lint, typecheck, unit tests
- Build Docker images (no push)
- Security scans

**On Push to `main`**:
- Full test suite
- Build and push Docker images to Artifact Registry
- Tag with `main-<git-sha>`
- Auto-deploy to production (after tests pass)

**On Git Tag (`v*`)**:
- Full test suite
- Build and push with semantic version tag
- Deploy to production
- Create GitHub release

**Manual Workflows**:
- Rollback to previous version
- Deploy specific commit to staging/production

### CI Workflow: Python Services

**File**: `.github/workflows/ci-python-services.yml`

**Stages**:
1. **Detect Changes**: Use `paths` filter to only run for changed services
2. **Lint & Type Check**: `ruff check`, `mypy`
3. **Unit Tests**: `pytest --cov` with coverage reporting
4. **Integration Tests**: Run against ephemeral PostgreSQL + Redis
5. **Build Docker Images**: Multi-stage build, tag with PR number
6. **Security Scan**: Trivy or Artifact Registry scan

**Matrix Strategy**: Run in parallel for each changed service

**Example**:
```yaml
name: CI - Python Services

on:
  pull_request:
    paths:
      - 'src/**'
      - '*_service/**'
      - 'celery-worker/**'
      - 'docker-compose.yml'

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            agent: src/agent_service/**
            journal: src/journal_service/**
            habits: habits_service/**
            # ... etc

  lint-and-test:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJSON(needs.detect-changes.outputs.services) }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install Poetry
        run: pipx install poetry
      - name: Install dependencies
        run: poetry install
      - name: Lint
        run: poetry run ruff check
      - name: Type check
        run: poetry run mypy
      - name: Test
        run: poetry run pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build-image:
    needs: lint-and-test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJSON(needs.detect-changes.outputs.services) }}
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - name: Build image
        run: |
          docker build -t ${{ matrix.service }}:pr-${{ github.event.number }} \
            -f ${{ matrix.service }}/Dockerfile .
```

### CD Workflow: Deploy Service

**File**: `.github/workflows/cd-deploy-service.yml`

**Stages**:
1. **Build & Push**: Multi-stage Docker build, push to Artifact Registry
2. **Tag Image**: `main-<git-sha>`, update `production-latest` alias
3. **Run Migrations**: Execute Alembic migrations via Cloud Run Job
4. **Deploy Service**: Update Cloud Run service with new image
5. **Health Check**: Verify service health endpoint
6. **Smoke Tests**: Run basic API tests against deployed service
7. **Rollback on Failure**: Revert to previous revision

**Reusable Workflow**:
```yaml
name: Deploy Service to Cloud Run

on:
  workflow_call:
    inputs:
      service_name:
        required: true
        type: string
      image_tag:
        required: true
        type: string
      environment:
        required: true
        type: string
    secrets:
      GCP_PROJECT_ID:
        required: true
      GCP_SERVICE_ACCOUNT_KEY:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ inputs.service_name }} \
            --image us-central1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/services/${{ inputs.service_name }}:${{ inputs.image_tag }} \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --set-secrets DATABASE_URL=database-url:latest

      - name: Health Check
        run: |
          SERVICE_URL=$(gcloud run services describe ${{ inputs.service_name }} --region us-central1 --format 'value(status.url)')
          curl -f ${SERVICE_URL}/health || exit 1
```

### Deployment Flow

**Main Branch Push**:
```
Push to main
    │
    ├─> CI: Test all services (parallel)
    │       │
    │       ├─> Lint ✓
    │       ├─> Type Check ✓
    │       ├─> Unit Tests ✓
    │       └─> Integration Tests ✓
    │
    ├─> Build & Push: Docker images (parallel per service)
    │       │
    │       ├─> Build multi-stage Dockerfile
    │       ├─> Tag: main-abc123
    │       ├─> Push to Artifact Registry
    │       └─> Vulnerability Scan
    │
    └─> Deploy: Cloud Run (sequential per service)
            │
            ├─> Migrations: Run Alembic (Cloud Run Job)
            ├─> Deploy: Update Cloud Run service
            ├─> Health Check: Verify /health endpoint
            ├─> Smoke Tests: Basic API validation
            └─> Tag: Update production-latest alias
```

**Rollback Flow**:
```
Manual trigger: rollback.yml
    │
    ├─> Select: Service + Target revision/tag
    ├─> Deploy: Cloud Run to previous image
    ├─> Health Check: Verify /health endpoint
    └─> Notify: Slack/email (optional)
```

---

## Docker Standardization

### Standard Dockerfile Pattern (All Services)

**Based on**: `habits_service/Dockerfile` ✅

**Template**:
```dockerfile
# ============================================
# Builder Stage: Install dependencies + build shared module
# ============================================
FROM python:3.12-slim as builder

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy service pyproject files
COPY {service}/pyproject.toml {service}/poetry.lock* ./

# Copy shared package
COPY ./src/shared /src/shared

# Install dependencies (no venv since we're in container)
RUN poetry config virtualenvs.create false \
    && poetry lock --no-interaction --no-ansi \
    && poetry install --no-root --only main --no-ansi

# Build shared module as wheel
WORKDIR /src/shared
RUN poetry build

# Install shared wheel into system Python
WORKDIR /app
RUN pip install /src/shared/dist/*.whl

# ============================================
# Runtime Stage: Minimal production image
# ============================================
FROM python:3.12-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY {service}/{module} /app/{module}

# Set Python path
ENV PYTHONPATH=/app:/app/src

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:{port}/health || exit 1

# Run application
CMD ["uvicorn", "{module}.app.main:app", "--host", "0.0.0.0", "--port", "{port}"]
```

### Service-Specific Configurations

| Service | Module | Port | CMD |
|---------|--------|------|-----|
| agent_service | agent_service.app | 8000 | `uvicorn agent_service.app.main:app --host 0.0.0.0 --port 8000` |
| journal_service | journal_service.journal_service | 8001 | `uvicorn journal_service.journal_service.main:app --host 0.0.0.0 --port 8001` |
| habits_service | habits_service.app | 8003 | `uvicorn habits_service.app.main:app --host 0.0.0.0 --port 8003` |
| meals_service | meals_service.meals_service | 8004 | `uvicorn meals_service.meals_service.web.app:app --host 0.0.0.0 --port 8004` |
| movements_service | movements_service.movements_service | 8005 | `uvicorn movements_service.movements_service.web.app:app --host 0.0.0.0 --port 8005` |
| practices_service | practices_service.practices_service | 8000 | `uvicorn practices_service.practices_service.web.app:app --host 0.0.0.0 --port 8000` |
| users_service | users_service.users_service | 8000 | `uvicorn users_service.users_service.web.app:app --host 0.0.0.0 --port 8000` |
| celery-worker | celery_worker.src | N/A | `celery -A tasks worker --loglevel=info` |

### Docker Compose Changes (Already Applied ✅)

All services now use:
- `context: .` (project root)
- `dockerfile: {service}/Dockerfile`

**Example**:
```yaml
agent_service:
  build:
    context: .
    dockerfile: src/agent_service/Dockerfile
  # ... rest of config
```

---

## Infrastructure as Code: infra-v2/ (OpenTofu)

### Philosophy

- **Production-first**: Build for production, duplicate for staging later
- **Modular design**: Reusable modules for services, databases, networking
- **Secure by default**: Least privilege IAM, Secret Manager, VPC
- **Stateful management**: Remote backend (GCS)
- **Environment parity**: Staging mirrors production (when created)

### Directory Structure

```
infra-v2/
├── bootstrap/
│   ├── 01-setup-secrets.sh            # One-time secret creation ✅
│   ├── 02-enable-apis.sh              # Enable GCP APIs
│   └── 03-create-artifact-registry.sh # Create container registry
├── modules/
│   ├── cloud-run-service/             # Reusable Cloud Run service
│   ├── cloud-sql-instance/            # PostgreSQL instance
│   ├── secret-volume/                 # Secret Manager volume mount
│   ├── vpc-connector/                 # Serverless VPC connector
│   └── iam-service-account/           # Service account with roles
├── environments/
│   ├── production/
│   │   ├── main.tf                    # Root module
│   │   ├── variables.tf               # Environment-specific vars
│   │   ├── terraform.tfvars           # Production values
│   │   ├── backend.tf                 # Remote state (GCS)
│   │   └── outputs.tf                 # Outputs (URLs, IPs, etc.)
│   └── staging/ (future)
│       └── ... (copy of production/)
├── shared/
│   ├── networks.tf                    # VPC, subnets, firewall rules
│   └── secrets.tf                     # Secret Manager resources
└── README.md
```

### Module: cloud-run-service

**Purpose**: Standardized Cloud Run Gen2 service deployment

**Features**:
- Secret volume mounts at `/secrets/<volume>/<file>`
- VPC connector for private DB access
- IAM bindings
- Environment variables
- Health checks
- Resource limits
- Autoscaling
- Traffic splitting (for canary deploys)

**Example Usage**:
```hcl
module "agent_service" {
  source = "../../modules/cloud-run-service"

  project_id       = var.project_id
  region           = var.region
  service_name     = "agent-service"
  image            = "us-central1-docker.pkg.dev/${var.project_id}/services/agent-service:${var.image_tag}"
  port             = 8000

  # Secret volume mounts
  secret_volumes = [
    {
      name        = "database-credentials"
      mount_path  = "/secrets/database"
      secret_name = "database-url"
    },
    {
      name        = "jwt-secret"
      mount_path  = "/secrets/jwt"
      secret_name = "jwt-secret"
    },
    {
      name        = "environment"
      mount_path  = "/secrets/environment"
      secret_name = "environment"
    }
  ]

  # Environment variables
  env_vars = {
    QDRANT_URL     = var.qdrant_url
    REDIS_URL      = var.redis_url
    OPENAI_API_KEY = var.openai_api_key
  }

  # Resource configuration
  cpu_limit    = "2"
  memory_limit = "2Gi"
  min_instances = 1
  max_instances = 10

  # VPC connector for private DB access
  vpc_connector = module.vpc_connector.id

  # Health check
  health_check_path = "/health"

  # IAM bindings
  allow_unauthenticated = true
}
```

### Module: cloud-sql-instance

**Purpose**: PostgreSQL database instance

**Features**:
- High availability (optional)
- Automated backups
- Private IP (VPC)
- Connection limits
- Resource sizing
- SSL enforcement
- Maintenance windows

**Example Usage**:
```hcl
module "main_database" {
  source = "../../modules/cloud-sql-instance"

  project_id       = var.project_id
  region           = var.region
  instance_name    = "mindmirror-main-db"
  database_version = "POSTGRES_15"
  tier             = "db-custom-2-7680"  # 2 vCPU, 7.5GB RAM

  databases = ["agent", "journal", "habits"]

  high_availability = true
  backup_enabled    = true
  backup_start_time = "03:00"

  # Private IP only
  ipv4_enabled    = false
  private_network = module.vpc.network_id

  # Connection limits
  max_connections = 100
}
```

### Production Environment Configuration

**File**: `infra-v2/environments/production/main.tf`

```hcl
terraform {
  required_version = ">= 1.6.0"

  backend "gcs" {
    bucket = "mindmirror-terraform-state"
    prefix = "production/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Networking
module "vpc" {
  source = "../../shared/networks"

  project_id = var.project_id
  region     = var.region
}

# Secrets
module "secrets" {
  source = "../../shared/secrets"

  project_id = var.project_id
}

# Databases
module "main_database" {
  source = "../../modules/cloud-sql-instance"
  # ... config
}

module "movements_database" {
  source = "../../modules/cloud-sql-instance"
  # ... config
}

module "practices_database" {
  source = "../../modules/cloud-sql-instance"
  # ... config
}

module "users_database" {
  source = "../../modules/cloud-sql-instance"
  # ... config
}

# Services
module "agent_service" {
  source = "../../modules/cloud-run-service"
  # ... config
}

module "journal_service" {
  source = "../../modules/cloud-run-service"
  # ... config
}

# ... repeat for all services
```

### Variables

**File**: `infra-v2/environments/production/variables.tf`

```hcl
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
}

variable "qdrant_url" {
  description = "Qdrant Cloud URL"
  type        = string
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
}

# ... etc
```

**File**: `infra-v2/environments/production/terraform.tfvars`

```hcl
project_id = "mindmirror-prod"
region     = "us-central1"
image_tag  = "production-latest"

# External services (Qdrant Cloud, etc.)
qdrant_url = "https://your-cluster.qdrant.io"
redis_url  = "redis://your-redis-instance:6379"
```

### Remote State Management

**Bootstrap State Bucket**:
```bash
# Run once
gsutil mb -p mindmirror-prod -l us-central1 gs://mindmirror-terraform-state
gsutil versioning set on gs://mindmirror-terraform-state
```

**Backend Config**: `infra-v2/environments/production/backend.tf`
```hcl
terraform {
  backend "gcs" {
    bucket = "mindmirror-terraform-state"
    prefix = "production/state"
  }
}
```

---

## Database Migration Automation

### Alembic in CI/CD

**Strategy**: Run migrations as Cloud Run Job before service deployment

**Why Cloud Run Job?**
- Runs in same network as Cloud SQL (private IP)
- Has access to Secret Manager
- Idempotent (safe to run multiple times)
- Logs available in Cloud Logging

### Migration Workflow

**File**: `.github/workflows/run-migrations.yml`

```yaml
name: Run Database Migrations

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      service:
        required: true
        type: string

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Run migration job
        run: |
          gcloud run jobs execute migrate-${{ inputs.service }} \
            --region us-central1 \
            --wait
```

### Migration Docker Image

**File**: `infra-v2/migrations/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy Alembic config
COPY src/alembic-config /app/alembic-config
COPY src/shared /app/shared

# Install dependencies
WORKDIR /app/alembic-config
RUN poetry install --no-root --only main

# Entrypoint: Run migrations
CMD ["poetry", "run", "alembic", "upgrade", "head"]
```

### Cloud Run Job Configuration (OpenTofu)

**Module**: `infra-v2/modules/migration-job/`

```hcl
resource "google_cloud_run_v2_job" "migration" {
  name     = "migrate-${var.service_name}"
  location = var.region

  template {
    template {
      containers {
        image = var.migration_image

        # Secret volume mounts
        volume_mounts {
          name       = "database-credentials"
          mount_path = "/secrets/database"
        }

        volume_mounts {
          name       = "environment"
          mount_path = "/secrets/environment"
        }
      }

      volumes {
        name = "database-credentials"
        secret {
          secret       = "database-url"
          default_mode = 0444
        }
      }

      volumes {
        name = "environment"
        secret {
          secret       = "environment"
          default_mode = 0444
        }
      }

      # VPC connector for private DB access
      vpc_access {
        connector = var.vpc_connector
        egress    = "PRIVATE_RANGES_ONLY"
      }

      service_account = var.service_account
      timeout         = "600s"  # 10 minutes max
    }
  }
}
```

### Deployment Order

```
1. Build & Push migration image
2. Run Cloud Run Job: migrate-{service}
3. Wait for job completion
4. Deploy Cloud Run service (if migrations succeed)
5. Health check deployed service
```

---

## Essential Observability

**Philosophy**: Pragmatic monitoring for solo/small team - skip enterprise bloat

### Cloud Logging (Built-in)

**What**: Automatic logging from Cloud Run services

**Setup**: Zero configuration needed ✅

**Usage**:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Request processed", extra={"user_id": user_id, "duration_ms": duration})
```

**Benefits**:
- Structured JSON logs
- Automatic log correlation (trace IDs)
- Search and filter in Cloud Console
- Log-based metrics (free quota: 50 GB/month)

**Query Examples**:
```sql
-- Find errors in agent service
resource.type="cloud_run_revision"
resource.labels.service_name="agent-service"
severity>=ERROR

-- Slow requests (>1s)
resource.type="cloud_run_revision"
jsonPayload.duration_ms>1000
```

### Error Reporting (Built-in)

**What**: Automatic error aggregation and alerting

**Setup**: Zero configuration for Python ✅

**Features**:
- Automatic exception capture from logs
- Error grouping and deduplication
- Occurrence tracking
- Email/Slack notifications (optional)

**Usage**: Just log exceptions with `logger.exception()`:
```python
try:
    process_request()
except Exception as e:
    logger.exception("Request processing failed", extra={"request_id": req_id})
    raise
```

### Cloud Monitoring (Basic Metrics)

**What**: Built-in metrics from Cloud Run

**Setup**: Zero configuration needed ✅

**Metrics Available**:
- Request count
- Request latency (p50, p95, p99)
- Container CPU utilization
- Container memory utilization
- Container instance count
- Billable container time

**Dashboard**: Auto-generated in Cloud Console

**Alerting** (Optional):
- Email on 5xx error rate > 5%
- Email on p95 latency > 2s
- Email on CPU > 80% for 5 minutes

### Health Checks (All Services)

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "agent-service",
  "version": "main-abc123",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "qdrant": "connected"
  }
}
```

**Implementation** (FastAPI):
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "agent-service",
        "version": os.getenv("IMAGE_TAG", "unknown"),
        "dependencies": await check_dependencies()
    }

async def check_dependencies() -> dict:
    checks = {}

    # Database
    try:
        async with db.session() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "disconnected"

    # Redis
    try:
        await redis.ping()
        checks["redis"] = "connected"
    except Exception:
        checks["redis"] = "disconnected"

    return checks
```

**Usage in CI/CD**:
```bash
# Wait for service to be healthy
SERVICE_URL=$(gcloud run services describe agent-service --region us-central1 --format 'value(status.url)')
for i in {1..30}; do
  curl -f ${SERVICE_URL}/health && break
  sleep 5
done
```

### Distributed Tracing (OpenTelemetry)

**Already Integrated**: `practices_service` has OpenTelemetry ✅

**Expand to All Services**:
```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to Cloud Trace
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)

# Usage
@app.post("/api/journal")
async def create_journal_entry(entry: JournalEntry):
    with tracer.start_as_current_span("create_journal_entry"):
        # ... your code
        pass
```

**Benefits**:
- Trace requests across microservices
- Identify bottlenecks
- View in Cloud Console (free quota: 2.5M spans/month)

### Cost Monitoring

**Setup**: Budget alerts in GCP Billing

**Recommended Budgets**:
- Cloud Run: $50/month
- Cloud SQL: $100/month
- Artifact Registry: $10/month
- **Total**: $200/month alert threshold

**Alerts**:
- Email at 50%, 75%, 90%, 100% of budget
- Slack notification (optional)

---

## Security Best Practices

### IAM Service Accounts

**Principle**: Least privilege - each service gets its own SA with minimal permissions

**Service Accounts**:
```
agent-service@mindmirror-prod.iam.gserviceaccount.com
  ├─ roles/cloudsql.client
  ├─ roles/secretmanager.secretAccessor
  └─ roles/storage.objectViewer

journal-service@mindmirror-prod.iam.gserviceaccount.com
  ├─ roles/cloudsql.client
  ├─ roles/secretmanager.secretAccessor
  └─ roles/storage.objectViewer

# ... repeat for each service
```

**GitHub Actions SA** (for CI/CD):
```
github-actions@mindmirror-prod.iam.gserviceaccount.com
  ├─ roles/run.admin
  ├─ roles/iam.serviceAccountUser
  ├─ roles/artifactregistry.writer
  └─ roles/cloudsql.admin (for migrations)
```

**Never**:
- Use default Compute Engine service account
- Grant `roles/owner` or `roles/editor`
- Share service account keys (use Workload Identity Federation for GitHub Actions)

### Secret Management

**All Secrets in Secret Manager** ✅

**Secret Organization**:
```
mindmirror-prod/
├─ database-url           (main DB)
├─ movements-database-url
├─ practices-database-url
├─ users-database-url
├─ jwt-secret
├─ openai-api-key
├─ qdrant-api-key
├─ supabase-service-role-key
└─ environment            (production/staging)
```

**Secret Versions**: Use `latest` alias for auto-rotation

**Access Control**:
```hcl
resource "google_secret_manager_secret_iam_member" "agent_db_access" {
  secret_id = google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:agent-service@mindmirror-prod.iam.gserviceaccount.com"
}
```

### Network Security

**VPC Connector**: All Cloud Run services in VPC

**Firewall Rules**:
- Cloud SQL: Private IP only, no public access
- Redis: Private IP only
- Cloud Run: Public HTTPS, private backends

**SSL/TLS**:
- Cloud Run: Automatic HTTPS
- Cloud SQL: SSL required for connections

### Container Security

**Base Image**: `python:3.12-slim` (minimal attack surface)

**Non-root User** (Optional Enhancement):
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

**Vulnerability Scanning**:
- Automatic via Artifact Registry
- Block deployments with CRITICAL vulnerabilities

**No Secrets in Images**:
- All secrets from Secret Manager
- Never `COPY .env` or hardcode credentials

---

## Deployment Procedures

### Initial Production Deployment

**Prerequisites**:
1. GCP project created (`mindmirror-prod`)
2. Billing enabled
3. GitHub secrets configured

**Step 1: Bootstrap Infrastructure**
```bash
cd infra-v2/bootstrap

# Enable required GCP APIs
./02-enable-apis.sh

# Create Artifact Registry
./03-create-artifact-registry.sh

# Create secrets (already done ✅)
./01-setup-secrets.sh
```

**Step 2: Deploy Infrastructure (OpenTofu)**
```bash
cd infra-v2/environments/production

# Initialize
tofu init

# Plan
tofu plan -out=tfplan

# Apply
tofu apply tfplan
```

**Step 3: Build & Push Images**
```bash
# Authenticate Docker
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build all services
docker compose build

# Tag and push
for service in agent journal habits meals movements practices users celery-worker mesh; do
  docker tag ${service}-service:latest \
    us-central1-docker.pkg.dev/mindmirror-prod/services/${service}-service:main-initial

  docker push us-central1-docker.pkg.dev/mindmirror-prod/services/${service}-service:main-initial
done
```

**Step 4: Run Migrations**
```bash
# Deploy migration job
cd infra-v2/modules/migration-job
tofu apply

# Execute migrations
gcloud run jobs execute migrate-main --region us-central1 --wait
```

**Step 5: Deploy Services**
```bash
# Update image tags in terraform.tfvars
image_tag = "main-initial"

# Apply
cd infra-v2/environments/production
tofu apply
```

**Step 6: Verify Deployment**
```bash
# Health checks
for service in agent journal habits meals movements practices users; do
  URL=$(gcloud run services describe ${service}-service --region us-central1 --format 'value(status.url)')
  curl -f ${URL}/health
done

# GraphQL Gateway
GATEWAY_URL=$(gcloud run services describe mesh-gateway --region us-central1 --format 'value(status.url)')
curl -f ${GATEWAY_URL}/graphql
```

### Regular Deployment (via CI/CD)

**Push to Main**:
```bash
git add .
git commit -m "feat: add new feature"
git push origin main
```

**CI/CD will automatically**:
1. Run tests
2. Build Docker images
3. Push to Artifact Registry
4. Run migrations
5. Deploy to Cloud Run
6. Run health checks
7. Notify on success/failure

### Hotfix Deployment

**Create Hotfix Branch**:
```bash
git checkout -b hotfix/critical-bug
# ... make fix
git commit -m "fix: critical bug"
git push origin hotfix/critical-bug
```

**Merge to Main (triggers auto-deploy)**:
```bash
gh pr create --base main --head hotfix/critical-bug
gh pr merge --auto --squash
```

**OR Manual Deploy**:
```bash
# Build and push
docker build -t agent-service:hotfix-abc123 -f src/agent_service/Dockerfile .
docker tag agent-service:hotfix-abc123 \
  us-central1-docker.pkg.dev/mindmirror-prod/services/agent-service:hotfix-abc123
docker push us-central1-docker.pkg.dev/mindmirror-prod/services/agent-service:hotfix-abc123

# Deploy
gcloud run deploy agent-service \
  --image us-central1-docker.pkg.dev/mindmirror-prod/services/agent-service:hotfix-abc123 \
  --region us-central1
```

### Rollback Procedure

**Automatic Rollback** (if health checks fail):
- CI/CD reverts to previous revision
- No manual intervention needed

**Manual Rollback**:
```bash
# List revisions
gcloud run revisions list --service agent-service --region us-central1

# Rollback to previous
gcloud run services update-traffic agent-service \
  --to-revisions agent-service-00042-abc=100 \
  --region us-central1
```

**OR use GitHub workflow**:
```bash
# Trigger rollback workflow
gh workflow run rollback.yml \
  -f service=agent-service \
  -f revision=00042
```

---

## GitHub Secrets Configuration

**Required Secrets** (Repository Settings → Secrets and variables → Actions):

```
GCP_PROJECT_ID           # mindmirror-prod
GCP_SERVICE_ACCOUNT_KEY  # JSON key for github-actions SA
ARTIFACT_REGISTRY_URL    # us-central1-docker.pkg.dev/mindmirror-prod/services
```

**Optional** (for notifications):
```
SLACK_WEBHOOK_URL        # For deployment notifications
```

---

## Cost Optimization

### Cloud Run

**Auto-scaling**:
- Min instances: 1 (avoid cold starts for critical services)
- Max instances: 10
- Concurrency: 80 requests per instance

**CPU Allocation**: "CPU is only allocated during request processing"

**Request Timeout**: 300s (adjust per service)

### Cloud SQL

**Right-sizing**:
- Start: `db-custom-2-7680` (2 vCPU, 7.5GB RAM)
- Monitor utilization, scale up if needed

**High Availability**: Production only, not staging

**Backups**: Daily at 3am UTC, retain 7 days

### Artifact Registry

**Image Retention**:
- Keep last 10 images per service
- Delete untagged after 30 days

**Storage**: ~5GB total (estimate)

### Estimated Monthly Costs

| Resource | Usage | Cost |
|----------|-------|------|
| Cloud Run (8 services) | 1M requests, 1GB RAM avg | $30 |
| Cloud SQL (4 instances) | db-custom-2-7680, HA | $250 |
| Artifact Registry | 5GB storage, 10GB egress | $5 |
| Cloud Logging | 10GB/month | Free tier |
| Cloud Monitoring | Basic metrics | Free tier |
| Secret Manager | 10 secrets, 1M accesses | $2 |
| **Total** | | **~$287/month** |

**Optimization Tips**:
- Use Cloud SQL proxy for connection pooling
- Reduce min instances to 0 for non-critical services
- Use Cloud CDN for static assets (web app)
- Monitor and right-size Cloud SQL instances

---

## Future Enhancements (Post-MVP)

### Staging Environment (Phase 2)
- Duplicate `infra-v2/environments/production/` to `staging/`
- Use smaller Cloud SQL instances
- Deploy on push to `staging` branch
- Manual promotion to production

### Advanced CI/CD
- Canary deployments (traffic splitting)
- Automated rollback on error rate spike
- Integration test suite against staging
- Performance regression tests

### Enhanced Observability
- Custom dashboards in Cloud Monitoring
- SLO/SLA tracking
- Distributed tracing across all services
- Log-based metrics and alerts

### Security Hardening
- Workload Identity Federation (no SA keys)
- Binary Authorization (signed images only)
- VPC Service Controls
- Secrets rotation automation

### Performance Optimization
- Cloud CDN for static assets
- Redis caching layer
- Database read replicas
- Connection pooling optimization

---

## Runbook: Common Operations

### View Service Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service" \
  --limit 50 \
  --format json
```

### Restart Service
```bash
gcloud run services update agent-service \
  --region us-central1 \
  --no-traffic  # Force new revision
```

### Scale Service
```bash
gcloud run services update agent-service \
  --region us-central1 \
  --min-instances 2 \
  --max-instances 20
```

### Update Secret
```bash
# Add new version
echo -n "new-secret-value" | gcloud secrets versions add database-url --data-file=-

# Services will pick up on next deployment or restart
```

### Database Maintenance
```bash
# Cloud SQL proxy for local access
cloud_sql_proxy -instances=mindmirror-prod:us-central1:main-db=tcp:5432

# Connect via psql
psql "host=127.0.0.1 port=5432 dbname=agent user=postgres"
```

### Manual Migration
```bash
# SSH into migration job
gcloud run jobs execute migrate-main --region us-central1 --wait

# View logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-main" --limit 50
```

---

## Success Criteria

**Phase 1: Production Deployment** ✅
- [ ] All services deployed to Cloud Run
- [ ] Databases migrated and running
- [ ] Health checks passing
- [ ] Secrets loaded from Secret Manager
- [ ] GraphQL Gateway federating all services
- [ ] Web app accessible via Cloud Run URL

**Phase 2: CI/CD Automation** 🎯
- [ ] GitHub Actions workflows created
- [ ] Push to main triggers automated deployment
- [ ] Tests run before deployment
- [ ] Migrations run automatically
- [ ] Rollback on deployment failure

**Phase 3: Observability** 📊
- [ ] Cloud Logging configured
- [ ] Error Reporting capturing exceptions
- [ ] Health checks on all services
- [ ] Basic alerts configured

**Phase 4: Documentation** 📚
- [ ] Deployment procedures documented
- [ ] Runbook created
- [ ] Rollback procedures tested
- [ ] Team onboarded

---

## Next Steps

1. **Review this strategy** - Validate approach and priorities
2. **Standardize Dockerfiles** - Apply habits pattern to all services
3. **Create OpenTofu modules** - Build reusable infrastructure components
4. **Implement CI/CD workflows** - GitHub Actions for build/test/deploy
5. **Bootstrap production** - Initial deployment to Cloud Run
6. **Validate and iterate** - Monitor, optimize, improve

---

**Document Owner**: DevOps Agent
**Last Review**: 2025-10-24
**Next Review**: After production deployment
