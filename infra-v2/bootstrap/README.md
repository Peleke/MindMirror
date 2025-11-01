# MindMirror Bootstrap Scripts

**Purpose:** Scripts to bootstrap production and staging GCP environments from scratch.

---

## 🎯 Quick Start

### Production Environment
```bash
# Run the orchestrator (sets up everything)
./bootstrap-production.sh

# This runs:
# 1. 07-bootstrap-cicd-infra.sh (Artifact Registry, State Bucket)
# 2. 06-bootstrap-wif.sh (Service Account, WIF)
```

### Staging Environment
```bash
# Run the orchestrator (sets up everything)
./bootstrap-staging.sh

# This runs:
# 1. 07-bootstrap-cicd-infra.sh (Artifact Registry, State Bucket)
# 2. 06-bootstrap-wif.sh (Service Account, WIF)
```

### Manual Setup (if needed)
```bash
# 1. Create GCP project (15 mins) - OPTIONAL
./00-create-gcp-project.sh

# 2. Create secrets (15 mins) - FOR FULL SETUP
./01-setup-secrets.sh

# 3. Create Supabase project (30 mins) - FOR FULL SETUP
./02-setup-supabase.sh

# 4. Run database migrations (15 mins) - FOR FULL SETUP
./03-run-migrations.sh

# 5. Apply RLS policies (10 mins) - FOR FULL SETUP
./04-apply-rls-policies.sh
```

**CI/CD Setup Time:** ~5 minutes (using orchestrators)
**Full Setup Time:** ~2 hours (including database/secrets)

---

## 📋 Scripts

### **bootstrap-production.sh** (RECOMMENDED)
Orchestrator that runs all required scripts for production CI/CD setup.

**What it does:**
1. Runs `07-bootstrap-cicd-infra.sh production`
2. Runs `06-bootstrap-wif.sh production`

**Prerequisites:**
- `gcloud` CLI authenticated
- Production project exists (`mindmirror-prod`)

**What it creates:**
- GCS state bucket: `mindmirror-tofu-state`
- Artifact Registry: `us-east4-docker.pkg.dev/mindmirror-prod/mindmirror`
- Service account: `github-actions-production@mindmirror-prod.iam.gserviceaccount.com`
- WIF pool and provider for GitHub Actions

---

### **bootstrap-staging.sh** (RECOMMENDED)
Orchestrator that runs all required scripts for staging CI/CD setup.

**What it does:**
1. Runs `07-bootstrap-cicd-infra.sh staging`
2. Runs `06-bootstrap-wif.sh staging`

**Prerequisites:**
- `gcloud` CLI authenticated
- Staging project exists (`mindmirror-69`)

**What it creates:**
- GCS state bucket: `mindmirror-tofu-state-staging`
- Artifact Registry: `us-east4-docker.pkg.dev/mindmirror-69/mindmirror`
- Service account: `github-actions-staging@mindmirror-69.iam.gserviceaccount.com`
- WIF pool and provider for GitHub Actions

---

### **07-bootstrap-cicd-infra.sh**
Creates CI/CD infrastructure (state bucket and artifact registry).

**Usage:**
```bash
./07-bootstrap-cicd-infra.sh [staging|production]
```

**What it creates:**
- GCS bucket with versioning for Terraform state
- Artifact Registry for Docker images
- Enables required GCP APIs

**Environment-aware:** Automatically configures bucket names and regions based on environment.

---

### **06-bootstrap-wif.sh**
Sets up Workload Identity Federation for GitHub Actions.

**Usage:**
```bash
./06-bootstrap-wif.sh [staging|production]
```

**What it creates:**
- Service account with proper roles
- WIF pool: `github-pool`
- WIF provider: `github-oidc`
- IAM bindings for GitHub Actions authentication

**Environment-aware:** Creates staging or production service accounts automatically.

---

### **00-create-gcp-project.sh** (LEGACY)
Creates new GCP project and links billing.

**Environment variables:**
- `PROJECT_ID` (optional) - Custom project ID, default: `swae-prod-TIMESTAMP`
- `BILLING_ACCOUNT_ID` (required if not interactive)
- `REGION` (optional) - Default: `us-central1`

**Outputs:**
- `.gcp-project-config` - Project configuration (source this in future shells)

---

### **05-bootstrap-gcp.sh** (LEGACY - use orchestrators instead)
Enables GCP APIs, creates state bucket, service accounts, Artifact Registry.

**Note:** This script is superseded by `07-bootstrap-cicd-infra.sh` and `06-bootstrap-wif.sh`.
Use the orchestrators (`bootstrap-production.sh` or `bootstrap-staging.sh`) instead.

---

### **01-setup-secrets.sh**
Creates all required secrets in Secret Manager.

**Prerequisites:**
- GCP project with Secret Manager API enabled (script 05 does this)

**Secrets created:**
- Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`
- Database: `DATABASE_URL`, `SUPABASE_CA_CERT_PATH`
- External services: `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `REDIS_URL`
- Internal: `REINDEX_SECRET_KEY`
- Service URLs: `AGENT_SERVICE_URL`, `JOURNAL_SERVICE_URL`, etc.

**Interactive:** Prompts for each secret value.

---

### **02-setup-supabase.sh**
Creates Supabase production project and stores credentials.

**Prerequisites:**
- Supabase account
- `supabase` CLI installed and authenticated

**Environment variables:**
- `SUPABASE_PROJECT_NAME` (optional) - Default: `swae-production`
- `SUPABASE_REGION` (optional) - Default: `us-east-1`

**Outputs:**
- Credentials stored in Secret Manager
- `env.production.supabase` - Local backup (DO NOT COMMIT)

**Manual step:** Project creation via Supabase dashboard (script guides you)

---

### **03-run-migrations.sh**
Runs Alembic migrations for all services.

**Prerequisites:**
- Supabase database created (script 02)
- `DATABASE_URL` set or available in Secret Manager
- `poetry` installed

**What it migrates:**
- Agent service (shared DB with journal)
- Habits service
- Movements service
- Practices service
- Users service

---

### **04-apply-rls-policies.sh**
Applies Row-Level Security policies to Supabase tables.

**Prerequisites:**
- Migrations complete (script 03)
- `psql` installed
- `DATABASE_URL` set or available in Secret Manager

**Tables protected:**
- `vouchers`
- `journal_entries`
- `habits`
- `practice_instances`
- `meals`
- `movements`

**Verification:** Script shows which tables have RLS enabled.

---

## 🔧 Configuration

### Customizing Project Settings

Edit variables at the top of each script:

```bash
# 00-create-gcp-project.sh
PROJECT_ID="swae-prod-$(date +%s)"  # Change naming scheme
REGION="us-central1"                # Change default region

# 02-setup-supabase.sh
SUPABASE_PROJECT_NAME="swae-production"
SUPABASE_REGION="us-east-1"
```

---

## 🚨 Troubleshooting

### Script fails with "project not found"

```bash
# Set project explicitly
gcloud config set project YOUR_PROJECT_ID
```

### Secret Manager permission denied

```bash
# Grant yourself Secret Manager admin role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:YOUR_EMAIL" \
  --role="roles/secretmanager.admin"
```

### Database connection fails

```bash
# Test connection
psql "$DATABASE_URL" -c "SELECT version();"

# Common issue: Supabase IP allowlist
# Fix: Check Supabase dashboard → Settings → Database → Connection Pooling
```

---

## 📚 Next Steps

After bootstrap is complete:

```bash
cd ../  # Back to infra-v2/

# Review variables
vim env.production.tfvars

# Initialize OpenTofu
tofu init

# Plan deployment
tofu plan -var-file=env.production.tfvars

# Apply
tofu apply -var-file=env.production.tfvars
```

See `../README.md` for OpenTofu deployment instructions.
