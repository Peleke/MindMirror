# Swae Production Bootstrap

**Purpose:** Scripts to bootstrap a production GCP environment from scratch.

---

## 🎯 Quick Start

Run these scripts in order:

```bash
# 1. Create GCP project (15 mins)
./00-create-gcp-project.sh

# 2. Bootstrap GCP infrastructure (15 mins)
./05-bootstrap-gcp.sh

# 3. Create secrets (15 mins)
./01-setup-secrets.sh

# 4. Create Supabase project (30 mins)
./02-setup-supabase.sh

# 5. Run database migrations (15 mins)
./03-run-migrations.sh

# 6. Apply RLS policies (10 mins)
./04-apply-rls-policies.sh
```

**Total time:** ~2 hours

---

## 📋 Scripts

### **00-create-gcp-project.sh**
Creates new GCP project and links billing.

**Environment variables:**
- `PROJECT_ID` (optional) - Custom project ID, default: `swae-prod-TIMESTAMP`
- `BILLING_ACCOUNT_ID` (required if not interactive)
- `REGION` (optional) - Default: `us-central1`

**Outputs:**
- `.gcp-project-config` - Project configuration (source this in future shells)

---

### **05-bootstrap-gcp.sh**
Enables GCP APIs, creates state bucket, service accounts, Artifact Registry.

**Prerequisites:**
- GCP project created (script 00)
- `gcloud` CLI authenticated

**What it creates:**
- GCS bucket: `swae-tofu-state`
- Artifact Registry: `swae` (Docker images)
- Service account for OpenTofu deployments
- Workload Identity Federation for GitHub Actions

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
