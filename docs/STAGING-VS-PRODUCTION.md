## Staging vs Production Separation
**Architecture**: Completely isolated environments via separate GCP projects + Supabase instances

---

## Environment Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         STAGING                              │
├─────────────────────────────────────────────────────────────┤
│  GCP Project:     mindmirror-staging (or use same project)  │
│  Supabase:        Separate staging instance                 │
│  Artifact Reg:    us-east4-docker.pkg.dev/mindmirror-staging│
│  Database:        Supabase PostgreSQL (staging)             │
│  Qdrant:          Qdrant Cloud (staging cluster)            │
│  Redis:           Upstash (staging instance)                │
│  Branch:          staging                                    │
│  Auto-deploy:     YES (no approval needed)                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       PRODUCTION                             │
├─────────────────────────────────────────────────────────────┤
│  GCP Project:     mindmirror-69                             │
│  Supabase:        Separate production instance              │
│  Artifact Reg:    us-east4-docker.pkg.dev/mindmirror-69     │
│  Database:        Supabase PostgreSQL (production)          │
│  Qdrant:          Qdrant Cloud (production cluster)         │
│  Redis:           Upstash (production instance)             │
│  Branch:          main                                       │
│  Auto-deploy:     NO (manual approval required)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Secret Management (Per Environment)

### GCP Secret Manager

**Staging Secrets** (in `mindmirror-staging` project):
```bash
# Database
DATABASE_URL              # Supabase staging PostgreSQL connection string

# Supabase (staging instance)
SUPABASE_URL              # https://your-staging-project.supabase.co
SUPABASE_ANON_KEY         # Staging anon key
SUPABASE_SERVICE_ROLE_KEY # Staging service role key
SUPABASE_JWT_SECRET       # Staging JWT secret
SUPABASE_CA_CERT_PATH     # CA cert for staging DB

# Qdrant (staging cluster)
QDRANT_URL                # https://your-staging-cluster.qdrant.io
QDRANT_API_KEY            # Staging API key

# Redis (staging)
REDIS_URL                 # redis://staging-redis.upstash.io:6379

# OpenAI (can share or separate)
OPENAI_API_KEY            # Staging OpenAI key (or shared)

# Service URLs (auto-populated after deploy)
AGENT_SERVICE_URL
JOURNAL_SERVICE_URL
HABITS_SERVICE_URL
MEALS_SERVICE_URL
CELERY_WORKER_URL

# Security
REINDEX_SECRET_KEY        # Staging reindex key
```

**Production Secrets** (in `mindmirror-69` project):
```bash
# Same structure, but production values
DATABASE_URL              # Supabase production PostgreSQL
SUPABASE_URL              # https://your-production-project.supabase.co
# ... etc (all production values)
```

### GitHub Secrets (for CI/CD)

**Required GitHub Repository Secrets**:
```
GCP_STAGING_SA_KEY        # Service account JSON for staging
GCP_PRODUCTION_SA_KEY     # Service account JSON for production
```

---

## Service Account Setup

### Staging Service Account

```bash
# Create service account for staging
gcloud iam service-accounts create github-actions-staging \
  --project=mindmirror-staging \
  --display-name="GitHub Actions - Staging"

# Grant permissions
gcloud projects add-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Create and download key
gcloud iam service-accounts keys create staging-key.json \
  --iam-account=github-actions-staging@mindmirror-staging.iam.gserviceaccount.com

# Add to GitHub secrets as GCP_STAGING_SA_KEY
```

### Production Service Account

```bash
# Create service account for production
gcloud iam service-accounts create github-actions-prod \
  --project=mindmirror-69 \
  --display-name="GitHub Actions - Production"

# Grant permissions (same as staging)
gcloud projects add-iam-policy-binding mindmirror-69 \
  --member="serviceAccount:github-actions-prod@mindmirror-69.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding mindmirror-69 \
  --member="serviceAccount:github-actions-prod@mindmirror-69.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding mindmirror-69 \
  --member="serviceAccount:github-actions-prod@mindmirror-69.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Create and download key
gcloud iam service-accounts keys create production-key.json \
  --iam-account=github-actions-prod@mindmirror-69.iam.gserviceaccount.com

# Add to GitHub secrets as GCP_PRODUCTION_SA_KEY
```

---

## Terraform/Tofu Variable Files

### How Separation Works

**Staging** (`infra/staging.auto.tfvars`):
```hcl
# Auto-generated by GitHub Actions
project_id           = "mindmirror-staging"
project_numerical_id = "1234567890"  # Staging project number
region               = "us-east4"

# Staging-specific config
environment = "staging"
log_level   = "DEBUG"
debug       = "true"

# Staging images (from staging Artifact Registry)
agent_service_container_image = "us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/agent_service:v1.0.0-abc123"
# ... etc
```

**Production** (`infra/production.auto.tfvars`):
```hcl
# Auto-generated by GitHub Actions
project_id           = "mindmirror-69"
project_numerical_id = "3858903851"  # Production project number
region               = "us-east4"

# Production-specific config
environment = "production"
log_level   = "INFO"
debug       = "false"

# Production images (from production Artifact Registry)
agent_service_container_image = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/agent_service:v1.0.0-abc123"
# ... etc
```

**Key Difference**: `project_id` variable controls which GCP project Terraform/Tofu deploys to.

---

## Secrets Flow (How Services Get Environment-Specific Secrets)

### Tofu Module Configuration

Services automatically read secrets from **their deployed GCP project**:

```hcl
# In infra/main.tf (works for both staging and production)
data "google_secret_manager_secret_version" "database_url" {
  secret  = "DATABASE_URL"
  project = var.project_id  # ← This is the key!
}

module "agent_service" {
  source = "./modules/agent_service"

  project_id   = var.project_id  # staging or production
  database_url = data.google_secret_manager_secret_version.database_url.secret_data
  # ... other secrets from Secret Manager in the SAME project
}
```

**Flow**:
1. Tofu reads `var.project_id` from auto.tfvars file
2. Fetches secrets from **that project's** Secret Manager
3. Passes secrets to Cloud Run service
4. Cloud Run service uses environment-specific secrets

### Creating Secrets Per Environment

```bash
# Staging
gcloud secrets create DATABASE_URL \
  --project=mindmirror-staging \
  --data-file=- <<EOF
postgresql://user:pass@staging.supabase.co:5432/postgres
EOF

# Production
gcloud secrets create DATABASE_URL \
  --project=mindmirror-69 \
  --data-file=- <<EOF
postgresql://user:pass@production.supabase.co:5432/postgres
EOF
```

**Result**: Same secret name (`DATABASE_URL`), different values per project.

---

## Deployment Workflow Differences

### Staging Deploy

```
Developer: git push origin staging
  ↓
GitHub Actions (staging-deploy.yml)
  ├─ Authenticates: GCP_STAGING_SA_KEY
  ├─ Pushes to: us-east4-docker.pkg.dev/mindmirror-staging/...
  ├─ Generates: infra/staging.auto.tfvars (project_id = mindmirror-staging)
  ├─ Commits: staging.auto.tfvars to staging branch
  ↓
Terrateam (staging workspace)
  ├─ Reads: staging.auto.tfvars
  ├─ Deploys to: mindmirror-staging GCP project
  ├─ Fetches secrets: mindmirror-staging Secret Manager
  ├─ Auto-applies: YES (no approval)
  ↓
Result: Staging environment updated
```

### Production Deploy

```
Developer: git push origin main
  ↓
GitHub Actions (production-deploy.yml)
  ├─ Authenticates: GCP_PRODUCTION_SA_KEY
  ├─ Pushes to: us-east4-docker.pkg.dev/mindmirror-69/...
  ├─ Generates: infra/production.auto.tfvars (project_id = mindmirror-69)
  ├─ Creates PR: With production.auto.tfvars changes
  ↓
Terrateam (production workspace)
  ├─ Reads: production.auto.tfvars
  ├─ Plans against: mindmirror-69 GCP project
  ├─ Posts plan: To PR for review
  ├─ Waits: For manual approval
  ↓
Human: Reviews plan → comments "terrateam apply"
  ↓
Terrateam
  ├─ Deploys to: mindmirror-69 GCP project
  ├─ Fetches secrets: mindmirror-69 Secret Manager
  ↓
Result: Production environment updated
```

---

## Supabase Separation

### Staging Supabase Instance

**URL**: `https://your-staging-project.supabase.co`

**Configuration**:
- Separate database instance
- Test data only
- Relaxed security policies (for testing)
- May share auth users with production OR separate

**Secrets to Create**:
```bash
gcloud secrets create SUPABASE_URL --project=mindmirror-staging --data-file=- <<EOF
https://your-staging-project.supabase.co
EOF

gcloud secrets create SUPABASE_ANON_KEY --project=mindmirror-staging --data-file=- <<EOF
your-staging-anon-key
EOF

# ... etc
```

### Production Supabase Instance

**URL**: `https://your-production-project.supabase.co`

**Configuration**:
- Separate database instance
- Real user data
- Strict security policies
- Production-grade performance tier

**Secrets to Create**:
```bash
gcloud secrets create SUPABASE_URL --project=mindmirror-69 --data-file=- <<EOF
https://your-production-project.supabase.co
EOF

# ... etc
```

---

## Testing the Separation

### Verify Staging Isolation

```bash
# 1. Deploy to staging
git push origin staging

# 2. Check staging Cloud Run services
gcloud run services list --project=mindmirror-staging --region=us-east4

# 3. Verify staging secrets
gcloud secrets list --project=mindmirror-staging

# 4. Test staging API
STAGING_URL=$(gcloud run services describe agent-service \
  --project=mindmirror-staging \
  --region=us-east4 \
  --format='value(status.url)')

curl $STAGING_URL/health
```

### Verify Production Isolation

```bash
# 1. Create production PR
git push origin main

# 2. Review Terrateam plan (should target mindmirror-69)
# 3. Approve deployment
# 4. Check production Cloud Run services
gcloud run services list --project=mindmirror-69 --region=us-east4

# 5. Verify production secrets (different from staging)
gcloud secrets list --project=mindmirror-69

# 6. Test production API
PROD_URL=$(gcloud run services describe agent-service \
  --project=mindmirror-69 \
  --region=us-east4 \
  --format='value(status.url)')

curl $PROD_URL/health
```

---

## Common Pitfalls

### ❌ **Wrong**: Sharing secrets across environments
```bash
# Don't do this!
gcloud secrets create DATABASE_URL --project=mindmirror-staging
# Then reference it from production → WRONG!
```

### ✅ **Right**: Separate secrets per project
```bash
gcloud secrets create DATABASE_URL --project=mindmirror-staging --data-file=staging-db.txt
gcloud secrets create DATABASE_URL --project=mindmirror-69 --data-file=production-db.txt
```

### ❌ **Wrong**: Hardcoding project IDs in Tofu modules
```hcl
# Don't do this!
resource "google_cloud_run_service" "agent" {
  project = "mindmirror-69"  # Hardcoded!
}
```

### ✅ **Right**: Use variable for project ID
```hcl
resource "google_cloud_run_service" "agent" {
  project = var.project_id  # From auto.tfvars
}
```

### ❌ **Wrong**: Using same Supabase instance
```
Staging services → production Supabase → Data contamination!
```

### ✅ **Right**: Separate Supabase instances
```
Staging services → staging Supabase (test data)
Production services → production Supabase (real data)
```

---

## Quick Reference

| Aspect | Staging | Production |
|--------|---------|------------|
| **GCP Project** | `mindmirror-staging` | `mindmirror-69` |
| **Supabase** | Separate instance | Separate instance |
| **Artifact Registry** | `mindmirror-staging/mindmirror` | `mindmirror-69/mindmirror` |
| **Secrets** | In staging project | In production project |
| **Branch** | `staging` | `main` |
| **Auto-deploy** | YES | NO (manual approval) |
| **Service Account** | `github-actions-staging` | `github-actions-prod` |
| **tfvars File** | `staging.auto.tfvars` | `production.auto.tfvars` |

---

## Summary

✅ **Complete isolation** via separate GCP projects
✅ **Separate Supabase instances** prevent data cross-contamination
✅ **Environment-specific secrets** via Secret Manager per project
✅ **Automatic separation** via `project_id` variable in Tofu
✅ **Safe deployments** via separate service accounts and approval gates

**The magic**: A single Tofu codebase (`infra/`) deploys to BOTH environments, controlled entirely by which `.auto.tfvars` file is used.
