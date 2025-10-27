# Sway (SWAE) Production Deployment Runbook

**Version:** 1.0
**Last Updated:** 2025-10-20
**Target:** EOD Production Launch (MVP)

---

## 📋 Overview

This runbook guides you through deploying Sway to production on Google Cloud Platform with Supabase. The process is broken into automated scripts and manual verification steps.

**Timeline:** 8-10 hours (EOD deployment)

---

## ✅ Prerequisites

### Required Tools

- [ ] **gcloud CLI** (>= 450.0.0)
  ```bash
  gcloud --version
  # Install: https://cloud.google.com/sdk/docs/install
  ```

- [ ] **OpenTofu** (>= 1.8.0)
  ```bash
  tofu version
  # Install: https://opentofu.org/docs/intro/install
  ```

- [ ] **Supabase CLI** (>= 1.100.0)
  ```bash
  supabase --version
  # Install: npm install -g supabase
  ```

- [ ] **psql** (PostgreSQL client)
  ```bash
  psql --version
  # Install: brew install postgresql (macOS) or apt-get install postgresql-client (Linux)
  ```

- [ ] **Poetry** (Python dependency manager)
  ```bash
  poetry --version
  # Install: https://python-poetry.org/docs/#installation
  ```

### Required Accounts & Access

- [ ] Google Cloud Platform account with billing enabled
- [ ] Supabase account (free tier acceptable for MVP)
- [ ] OpenAI API key (for LLM/embeddings)
- [ ] Qdrant Cloud account (or self-hosted Qdrant)
- [ ] Redis instance (Upstash free tier or managed Redis)

### Required Credentials

Have these ready before starting:
- [ ] **GCP Billing Account ID**
- [ ] **OpenAI API Key** (`sk-...`)
- [ ] **Qdrant URL** and **API Key**
- [ ] **Redis URL** (e.g., `redis://...`)

---

## 🚀 Deployment Process

### Phase 1: GCP Project Setup (30-45 minutes)

#### Step 1.1: Create GCP Project

**Script:** `scripts/00-create-gcp-project.sh`

```bash
# Set your billing account ID
export BILLING_ACCOUNT_ID="XXXXXX-XXXXXX-XXXXXX"

# Optional: customize project ID
export PROJECT_ID="swae-prod-$(date +%s)"
export REGION="us-central1"

# Run script
./scripts/00-create-gcp-project.sh
```

**What it does:**
- Creates new GCP project
- Links billing account
- Enables essential APIs
- Saves configuration to `.gcp-project-config`

**Verify:**
```bash
source .gcp-project-config
gcloud config get-value project  # Should show your new project ID
```

---

#### Step 1.2: Bootstrap GCP Infrastructure

**Script:** `infra/bootstrap.sh`

```bash
cd infra
./bootstrap.sh
cd ..
```

**What it does:**
- Enables all required GCP APIs (Cloud Run, Secret Manager, etc.)
- Creates GCS bucket for OpenTofu state (`swae-tofu-state`)
- Creates service account for OpenTofu deployments
- Configures Workload Identity Federation for GitHub Actions
- Sets up Artifact Registry for Docker images

**Verify:**
```bash
# Check state bucket exists
gsutil ls gs://swae-tofu-state

# Check Artifact Registry
gcloud artifacts repositories list --location=$REGION
```

---

#### Step 1.3: Create Secrets in Secret Manager

**Script:** `scripts/01-setup-secrets.sh`

```bash
./scripts/01-setup-secrets.sh
```

**What it does:**
- Prompts for all required secret values
- Creates secrets in GCP Secret Manager
- Auto-generates random keys where appropriate (e.g., `REINDEX_SECRET_KEY`)
- Creates placeholder secrets for service URLs (updated after deployment)

**Secrets you'll be prompted for:**
- `SUPABASE_URL` - Get this in Step 2
- `SUPABASE_ANON_KEY` - Get this in Step 2
- `SUPABASE_SERVICE_ROLE_KEY` - Get this in Step 2
- `SUPABASE_JWT_SECRET` - Get this in Step 2
- `DATABASE_URL` - Get this in Step 2
- `OPENAI_API_KEY` - Have ready
- `QDRANT_URL` - Have ready
- `QDRANT_API_KEY` - Have ready
- `REDIS_URL` - Have ready

**Verify:**
```bash
# List all secrets
gcloud secrets list --project=$PROJECT_ID

# Test accessing a secret
gcloud secrets versions access latest --secret="OPENAI_API_KEY"
```

---

### Phase 2: Supabase Setup (30-60 minutes)

#### Step 2.1: Create Supabase Project

**Script:** `scripts/02-setup-supabase.sh`

```bash
export SUPABASE_PROJECT_NAME="swae-production"
export SUPABASE_REGION="us-east-1"

./scripts/02-setup-supabase.sh
```

**What it does:**
- Authenticates with Supabase CLI
- Guides you through project creation (manual step in Supabase dashboard)
- Retrieves project credentials
- Stores credentials in GCP Secret Manager
- Saves backup to `env.production.supabase` (DO NOT COMMIT)

**Manual Steps (guided by script):**
1. Open https://app.supabase.com/new
2. Create project: `swae-production`
3. Region: `us-east-1` (or preferred region)
4. **Generate strong database password** (save it!)
5. Wait ~2 minutes for provisioning
6. Retrieve API keys from: https://app.supabase.com/project/YOUR_PROJECT_ID/settings/api
7. Retrieve database URL from: https://app.supabase.com/project/YOUR_PROJECT_ID/settings/database

**Verify:**
```bash
# Test database connection
psql "$DATABASE_URL" -c "SELECT version();"

# Should output PostgreSQL version
```

---

#### Step 2.2: Run Database Migrations

**Script:** `scripts/03-run-migrations.sh`

```bash
# Ensure DATABASE_URL is set
export DATABASE_URL="postgres://..."  # Or source env.production.supabase

./scripts/03-run-migrations.sh
```

**What it does:**
- Runs Alembic migrations for all services:
  - Agent service (journal + agent shared DB)
  - Habits service
  - Movements service
  - Practices service
  - Users service
- Creates all required tables and indexes

**Verify:**
```bash
# Check tables exist
psql "$DATABASE_URL" -c "\dt"

# Should show: vouchers, journal_entries, habits, practice_instances, meals, movements, users, etc.
```

---

#### Step 2.3: Apply RLS Policies

**Script:** `scripts/04-apply-rls-policies.sh`

```bash
./scripts/04-apply-rls-policies.sh
```

**What it does:**
- Enables Row-Level Security on all user-facing tables
- Creates policies ensuring users can only access their own data
- Creates service role bypass for admin operations
- Verifies RLS is enabled

**Tables protected:**
- `vouchers`
- `journal_entries`
- `habits`
- `practice_instances` (workouts)
- `meals`
- `movements`

**Verify:**
```bash
# Check RLS is enabled
psql "$DATABASE_URL" -c "
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;
"

# All user-facing tables should show rowsecurity = t
```

**Test RLS:**
```bash
# 1. Create test user in Supabase dashboard
# 2. Get user JWT token
# 3. Try to query as user (should only see own data)

# Example test query (replace JWT):
psql "$DATABASE_URL" -c "
SET request.jwt.claims = '{\"sub\":\"test-user-id\"}';
SELECT * FROM vouchers;  -- Should only show vouchers for test-user-id
"
```

---

### Phase 3: Infrastructure Deployment (3-5 hours)

#### Step 3.1: Create infra-v2 OpenTofu Code

**This is where you build the Cloud Run v2 modules with secret volume mounts.**

Key changes from current `infra/`:
1. **Resource type:** `google_cloud_run_v2_service` (not v1)
2. **Secret mounting:** Volume mounts (not env vars)
3. **Min instances:** Set to 1 for `users_service`, `gateway`, `agent_service`
4. **Health checks:** Startup + liveness probes

**Directory structure:**
```
infra-v2/
├── main.tf                    # Root module
├── variables.tf               # Input variables
├── outputs.tf                 # Service URLs
├── versions.tf                # Provider versions
├── base/                      # Base infrastructure
│   ├── main.tf                # GCS, service accounts, IAM
│   ├── variables.tf
│   └── outputs.tf
├── modules/
│   ├── cloud-run-v2/          # Reusable Cloud Run v2 module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── agent_service/
│   ├── journal_service/
│   ├── habits_service/
│   ├── meals_service/
│   ├── movements_service/
│   ├── practices_service/
│   ├── users_service/
│   ├── gateway/
│   └── celery_worker/
└── env.production.tfvars      # Production variables
```

**Example Cloud Run v2 module with secret volumes:**

```hcl
# infra-v2/modules/cloud-run-v2/main.tf
resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    # Min instances (critical services only)
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # Service account
    service_account = var.service_account_email

    # Secret volumes
    dynamic "volumes" {
      for_each = var.secrets
      content {
        name = volumes.value.name
        secret {
          secret = volumes.value.secret_name
          items {
            version = "latest"
            path    = volumes.value.filename
          }
        }
      }
    }

    containers {
      image = var.image

      # Volume mounts
      dynamic "volume_mounts" {
        for_each = var.secrets
        content {
          name       = volume_mounts.value.name
          mount_path = "/secrets/${volume_mounts.value.name}"
        }
      }

      # Environment variables (non-secret config only)
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.value.name
          value = env.value.value
        }
      }

      # Health checks
      startup_probe {
        http_get {
          path = "/health"
          port = var.port
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = var.port
        }
        initial_delay_seconds = 0
        timeout_seconds       = 3
        period_seconds        = 30
        failure_threshold     = 3
      }

      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }
    }
  }

  # Ingress control
  ingress = var.ingress  # "INGRESS_TRAFFIC_ALL" or "INGRESS_TRAFFIC_INTERNAL_ONLY"

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# IAM (conditional - only if public access needed)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.allow_unauthenticated ? 1 : 0

  project  = google_cloud_run_v2_service.service.project
  location = google_cloud_run_v2_service.service.location
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" {
  value = google_cloud_run_v2_service.service.uri
}
```

**Example usage (users_service):**

```hcl
# infra-v2/modules/users_service/main.tf
module "users_service" {
  source = "../cloud-run-v2"

  service_name          = "users-service"
  project_id            = var.project_id
  region                = var.region
  image                 = var.users_image
  service_account_email = var.service_account_email

  # Critical service - no cold starts
  min_instances = 1
  max_instances = 10

  # Public access (for now - will be INTERNAL_ONLY after VPC setup)
  ingress               = "INGRESS_TRAFFIC_ALL"
  allow_unauthenticated = true

  # Secret volume mounts
  secrets = [
    {
      name        = "database-url"
      secret_name = "DATABASE_URL"
      filename    = "database-url"
    },
    # Add other secrets as needed
  ]

  # Non-secret environment variables
  env_vars = [
    {
      name  = "ENVIRONMENT"
      value = "production"
    },
    {
      name  = "LOG_LEVEL"
      value = "info"
    },
  ]

  port         = 8000
  cpu_limit    = "1000m"
  memory_limit = "512Mi"
}
```

---

#### Step 3.2: Update Application Code for Secret Files

**Services need to read secrets from files instead of environment variables.**

**Example (Python FastAPI services):**

```python
# Before (env vars):
import os
openai_api_key = os.getenv("OPENAI_API_KEY")
database_url = os.getenv("DATABASE_URL")

# After (volume mounts):
def read_secret(secret_name: str) -> str:
    """Read secret from volume mount."""
    secret_path = f"/secrets/{secret_name}/{secret_name}"
    try:
        with open(secret_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback to env var for local development
        return os.getenv(secret_name.upper().replace('-', '_'), '')

openai_api_key = read_secret("openai-api-key")
database_url = read_secret("database-url")
```

**Update services:**
- `src/agent_service/app/config.py`
- `src/journal_service/journal_service/config.py`
- `habits_service/habits_service/app/config.py`
- `meals_service/meals_service/config.py`
- `movements_service/movements_service/config.py`
- `practices_service/practices/config.py`
- `users_service/users_service/config.py`
- `mesh/gateway.config.ts` (Node.js - use `fs.readFileSync`)

**Commit these changes before deployment!**

---

#### Step 3.3: Initialize OpenTofu

```bash
cd infra-v2

# Initialize with GCS backend
tofu init \
  -backend-config="bucket=swae-tofu-state" \
  -backend-config="prefix=production/state"
```

**Verify:**
```bash
tofu providers
# Should show: hashicorp/google ~> 5.0
```

---

#### Step 3.4: Plan Deployment

```bash
# Create production variables file
cat > env.production.tfvars <<EOF
project_id     = "swae-prod-XXXXXX"
region         = "us-central1"
environment    = "production"

# Container images (update with your registry)
agent_service_image    = "us-central1-docker.pkg.dev/PROJECT/swae/agent-service:latest"
journal_service_image  = "us-central1-docker.pkg.dev/PROJECT/swae/journal-service:latest"
# ... other images

# Service-specific config
min_instances_critical = 1  # users, gateway, agent
min_instances_normal   = 0  # others
EOF

# Run plan
tofu plan -var-file=env.production.tfvars -out=production.tfplan
```

**Review the plan carefully!**
- Check all 8 services will be created
- Verify secret volume mounts are configured
- Confirm min_instances settings

---

#### Step 3.5: Deploy to Production

```bash
# Backup current state (if any)
mkdir -p ../backups
tofu state pull > ../backups/state-$(date +%Y%m%d-%H%M%S).json

# Apply deployment
tofu apply production.tfplan
```

**What gets deployed:**
- 8 Cloud Run v2 services (agent, journal, habits, meals, movements, practices, users, gateway)
- 1 Celery worker (Pub/Sub triggered)
- All with secret volume mounts
- Min instances on critical services

**Expected duration:** 5-10 minutes

---

#### Step 3.6: Update Service URL Secrets

After deployment, service URLs need to be stored in Secret Manager so services can communicate:

```bash
# Get deployed service URLs
GATEWAY_URL=$(tofu output -raw gateway_url)
AGENT_URL=$(tofu output -raw agent_service_url)
JOURNAL_URL=$(tofu output -raw journal_service_url)
# ... etc

# Update secrets
echo -n "$AGENT_URL" | gcloud secrets versions add AGENT_SERVICE_URL --data-file=-
echo -n "$JOURNAL_URL" | gcloud secrets versions add JOURNAL_SERVICE_URL --data-file=-
# ... repeat for all services

# Trigger redeployment to pick up new URLs
tofu apply -var-file=env.production.tfvars -auto-approve
```

---

### Phase 4: Validation & Testing (1-2 hours)

#### Step 4.1: Health Checks

```bash
# Check all services are healthy
GATEWAY_URL=$(tofu output -raw gateway_url)
curl -f "$GATEWAY_URL/healthcheck" || echo "Gateway FAILED"

AGENT_URL=$(tofu output -raw agent_service_url)
curl -f "$AGENT_URL/health" || echo "Agent FAILED"

# ... repeat for all services
```

**All should return 200 OK.**

---

#### Step 4.2: GraphQL Gateway Test

```bash
# Test GraphQL schema is federated
curl -X POST "$GATEWAY_URL/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ __schema { queryType { name } } }"
  }'

# Should return valid GraphQL introspection response
```

---

#### Step 4.3: End-to-End Voucher Flow

**Manual test:**
1. Open web app (deployed separately): `https://swae-web.run.app`
2. Navigate to `/admin/vouchers/create`
3. Create magic link voucher
4. Use magic link to sign up
5. Complete onboarding
6. Log a workout
7. Check journal entry is created

**Verify in Supabase dashboard:**
- User exists in `auth.users`
- Voucher exists in `vouchers` table
- Practice instances logged in `practice_instances`
- RLS policies prevent accessing other users' data

---

## 🔧 Troubleshooting

### Service Won't Start

**Symptom:** Cloud Run service shows "container failed to start"

**Check:**
```bash
# View service logs
gcloud run services logs read SERVICE_NAME --region=$REGION --limit=50

# Common issues:
# 1. Secret not mounted (permission denied)
# 2. Health check failing (port mismatch)
# 3. Missing environment variable
```

**Fix:**
- Verify service account has `secretmanager.secretAccessor` role
- Check health check endpoint returns 200
- Ensure all required secrets exist

---

### Database Connection Fails

**Symptom:** Services crash with "could not connect to database"

**Check:**
```bash
# Test DATABASE_URL from secret
DATABASE_URL=$(gcloud secrets versions access latest --secret="DATABASE_URL")
psql "$DATABASE_URL" -c "SELECT 1"
```

**Fix:**
- Verify DATABASE_URL format: `postgresql://user:pass@host:5432/db?sslmode=require`
- Check Supabase IP allowlist (should allow Cloud Run IPs)
- Verify CA cert path if using custom SSL

---

### Service URL Circular Dependency

**Symptom:** Services can't find each other

**Solution:**
This is expected on first deployment. Run the update script:

```bash
cd infra-v2
./scripts/update-service-urls.sh  # You'll need to create this

# Or manually:
tofu output -json | jq -r '.[] | .value' | while read url; do
  # Update secrets with service URLs
  # Then redeploy
done
```

---

## 📊 Post-Deployment

### Monitor Services

**Cloud Run Console:**
https://console.cloud.google.com/run?project=$PROJECT_ID

**View logs:**
```bash
gcloud run services logs read gateway --region=$REGION --follow
```

**Set up monitoring:**
1. Cloud Run metrics (automatic)
2. Log-based alerts
3. Uptime checks

---

### Cost Monitoring

**Estimate:** ~$50-100/month for 3-10 alpha users

**Monitor:**
```bash
# View current month costs
gcloud billing projects describe $PROJECT_ID

# Set budget alert
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT_ID \
  --display-name="Swae Production Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=90
```

---

## 🚨 Rollback Procedure

If deployment fails catastrophically:

```bash
# Restore previous state
cd infra-v2
tofu state push ../backups/state-TIMESTAMP.json

# Or destroy and redeploy
tofu destroy -var-file=env.production.tfvars
# Fix issues, then redeploy
```

---

## 📝 Next Steps (Post-MVP)

After successful MVP deployment, proceed with hardening:

1. **VPC Isolation** (Story 3.3)
   - Create VPC connector
   - Set mesh services to `INGRESS_TRAFFIC_INTERNAL_ONLY`
   - Configure gateway to use VPC egress

2. **Gateway Auth Enhancement** (Story 3.4a)
   - Implement JWT → users_service ID exchange
   - Add Redis caching
   - Remove client header trust

3. **CI/CD Pipeline** (Story 3.6)
   - GitHub Actions workflow
   - Tag-triggered deployments
   - Non-blocking tests
   - Manual approval gate

---

## 🎯 Success Criteria

MVP deployment is successful when:

- [x] All 8 services deployed to Cloud Run v2
- [x] Health checks pass for all services
- [x] Gateway federates all microservice schemas
- [x] Voucher flow works end-to-end
- [x] RLS policies prevent cross-user data access
- [x] Secrets mounted as volumes (not env vars)
- [x] Critical services have min_instances=1 (no cold starts)
- [x] Costs under $100/month projected
- [x] No P0 security issues (HTTPS, Supabase auth, RLS)

---

## 📚 References

- **Epic 3:** `docs/epics/epic-3-infrastructure.md`
- **Cloud Run v2:** https://cloud.google.com/run/docs/configuring/services
- **Secret Manager:** https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets
- **Supabase RLS:** https://supabase.com/docs/guides/auth/row-level-security
- **OpenTofu:** https://opentofu.org/docs/

---

**Questions? Issues?**
Check `docs/epics/epic-3-infrastructure.md` or review automation scripts in `scripts/`.
