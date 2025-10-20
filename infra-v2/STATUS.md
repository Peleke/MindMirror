# infra-v2 Status Report

**Created:** 2025-10-20
**Status:** Ready for Review & Completion
**Target:** EOD Production Deployment (8-10 hours)

---

## ✅ What's Complete

### Bootstrap Scripts (infra-v2/bootstrap/)
- ✅ `00-create-gcp-project.sh` - GCP project creation + billing
- ✅ `05-bootstrap-gcp.sh` - APIs, state bucket, service accounts, WIF
- ✅ `01-setup-secrets.sh` - Secret Manager setup (interactive)
- ✅ `02-setup-supabase.sh` - Supabase project creation (guided)
- ✅ `03-run-migrations.sh` - Alembic migrations (all services)
- ✅ `04-apply-rls-policies.sh` - Row-Level Security policies
- ✅ `bootstrap/README.md` - Full instructions

### OpenTofu Infrastructure
- ✅ **Root Module:**
  - `main.tf` - Orchestrates all services
  - `variables.tf` - Input variables
  - `outputs.tf` - Service URLs
  - `versions.tf` - Provider config + backend
  - `env.production.tfvars.example` - Example configuration

- ✅ **Base Module** (`modules/base/`)
  - Service accounts for all 7 services
  - IAM bindings
  - GCS bucket for traditions

- ✅ **Reusable Cloud Run v2 Module** (`modules/cloud-run-v2/`)
  - Secret volume mounts
  - Health checks (startup + liveness)
  - Configurable scaling
  - IAM configuration

- ✅ **Users Service Module** (`modules/users_service/`)
  - Complete reference implementation
  - Shows how to use cloud-run-v2 module
  - Secret volume mounting example
  - Min instances = 1 (no cold starts)

- ✅ **Service Module Template** (`modules/_TEMPLATE_SERVICE/`)
  - `main.tf.template` with comprehensive comments
  - `variables.tf.template`
  - `outputs.tf.template`
  - Instructions for duplicating

### Documentation
- ✅ `infra-v2/README.md` - Comprehensive guide
- ✅ `bootstrap/README.md` - Bootstrap instructions
- ✅ `docs/PRODUCTION-DEPLOYMENT-RUNBOOK.md` - End-to-end deployment guide

---

## ⚠️ What Needs Completion

### Service Modules (Use Template)

**Remaining modules to complete:**
1. `agent_service/` - Copy from template
2. `journal_service/` - Copy from template
3. `habits_service/` - Copy from template
4. `meals_service/` - Copy from template
5. `movements_service/` - Copy from template
6. `practices_service/` - Copy from template
7. `gateway/` - Copy from template
8. `celery_worker/` - Copy from template

**How to complete:**
```bash
# For each service:
cp -r modules/_TEMPLATE_SERVICE modules/agent_service
cd modules/agent_service
mv main.tf.template main.tf
mv variables.tf.template variables.tf
mv outputs.tf.template outputs.tf

# Search & replace SERVICE_NAME → agent
# Update secret_volumes with secrets needed by service
# Update env_vars with service-specific config
```

**Reference:** `modules/users_service/` (complete example)

---

### Application Code Updates

**Services need to read secrets from files:**

#### Python Services (8 services)
**Files to update:**
- `src/agent_service/app/config.py`
- `src/journal_service/journal_service/config.py`
- `habits_service/habits_service/app/config.py`
- `meals_service/meals_service/config.py`
- `movements_service/movements_service/config.py`
- `practices_service/practices/config.py`
- `users_service/users_service/config.py`

**Pattern:**
```python
def read_secret(secret_name: str) -> str:
    secret_path = f"/secrets/{secret_name}/{secret_name}"
    try:
        with open(secret_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.getenv(secret_name.upper().replace('-', '_'), '')

# Usage:
database_url = read_secret("database-url")
openai_key = read_secret("openai-api-key")
```

#### Node.js Service (Gateway)
**File to update:**
- `mesh/gateway.config.ts`

**Pattern:**
```javascript
function readSecret(secretName) {
  try {
    return fs.readFileSync(`/secrets/${secretName}/${secretName}`, 'utf8').trim();
  } catch (error) {
    return process.env[secretName.toUpperCase().replace(/-/g, '_')];
  }
}

const supabaseJwtSecret = readSecret('supabase-jwt-secret');
```

---

### Docker Images

**Need to build and push:**
1. agent-service
2. journal-service
3. habits-service
4. meals-service
5. movements-service
6. practices-service
7. users-service
8. gateway
9. celery-worker

**Example:**
```bash
# After running bootstrap/05-bootstrap-gcp.sh:
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Build & push each service:
cd src/agent_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/agent-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/agent-service:latest

# Repeat for all services
```

---

## 📋 Deployment Checklist

### Phase 1: Bootstrap (2 hours)
- [ ] Customize bootstrap scripts (replace "MindMirror" → "Swae")
- [ ] Run `00-create-gcp-project.sh`
- [ ] Run `05-bootstrap-gcp.sh`
- [ ] Run `01-setup-secrets.sh` (have OpenAI, Qdrant, Redis creds ready)
- [ ] Run `02-setup-supabase.sh` (create project in dashboard)
- [ ] Run `03-run-migrations.sh`
- [ ] Run `04-apply-rls-policies.sh`

### Phase 2: Code Preparation (2-3 hours)
- [ ] Complete 8 service modules (copy from template)
- [ ] Update app code to read secrets from files (Python)
- [ ] Update gateway code to read secrets from files (Node.js)
- [ ] Build all 9 Docker images
- [ ] Push images to Artifact Registry

### Phase 3: Infrastructure (1-2 hours)
- [ ] Create `env.production.tfvars` from example
- [ ] Update project_id and image URLs
- [ ] Run `tofu init`
- [ ] Run `tofu plan -var-file=env.production.tfvars`
- [ ] Review plan carefully
- [ ] Run `tofu apply -var-file=env.production.tfvars`

### Phase 4: Post-Deployment (1 hour)
- [ ] Update service URL secrets with deployed URLs
- [ ] Redeploy to pick up correct URLs
- [ ] Test all health checks
- [ ] Test GraphQL gateway introspection
- [ ] Test end-to-end voucher flow

**Total estimated time:** 6-8 hours

---

## 🎯 Key Decisions Made

### Secret Management
**Decision:** Volume mounts (not environment variables)
**Rationale:**
- More secure (not visible in logs/env)
- Cloud Run v2 best practice
- Supports secret rotation

**Effort:** 2-3 hours (added to MVP)

### RLS Policies
**Decision:** Include in MVP
**Rationale:**
- Database-level security
- Prevents data leaks even if app code has bugs
- Relatively quick to implement (1-2 hours)

**Effort:** 1-2 hours (added to MVP)

### VPC Isolation
**Decision:** Defer to Phase 2 (hardening)
**Rationale:**
- Complex (4-6 hours)
- Not blocking for basic functionality
- Can add incrementally after MVP

**Effort:** Deferred to tomorrow

### Gateway Auth
**Decision:** Defer to Phase 2 (hardening)
**Rationale:**
- Code changes required (4-5 hours)
- Current auth works (just less secure)
- Can add incrementally after MVP

**Effort:** Deferred to tomorrow

---

## 📊 Architecture Comparison

### infra/ (Old - Cloud Run v1)
- Cloud Run v1 (deprecated)
- Secrets as environment variables (INSECURE)
- No min instances (cold starts)
- All services publicly accessible
- No RLS policies

### infra-v2/ (New - Cloud Run v2)
- ✅ Cloud Run v2 (modern, performant)
- ✅ Secrets as volume mounts (SECURE)
- ✅ Min instances = 1 for critical services (no cold starts)
- ✅ RLS policies (database-level security)
- ⏳ VPC isolation (Phase 2)
- ⏳ Gateway auth (Phase 2)

---

## 🔍 What to Review

### Bootstrap Scripts
**Location:** `infra-v2/bootstrap/`
**Focus:**
- Script order (00, 05, 01, 02, 03, 04)
- Secret names match your services
- Supabase region preference
- RLS policies cover all tables

### OpenTofu Modules
**Location:** `infra-v2/modules/`
**Focus:**
- `users_service/` - Reference implementation
- `_TEMPLATE_SERVICE/` - Comments helpful?
- `cloud-run-v2/` - Reusable module correct?

### Main Orchestration
**Location:** `infra-v2/main.tf`
**Focus:**
- Service dependencies correct?
- Secret data sources complete?
- Module parameters correct?

### Documentation
**Location:** `infra-v2/README.md`
**Focus:**
- Instructions clear?
- Examples helpful?
- Missing any steps?

---

## 💡 Recommendations

### Immediate (Before Running Scripts)
1. **Review bootstrap scripts** - Customize naming, region preferences
2. **Gather credentials** - Have OpenAI, Qdrant, Redis keys ready
3. **Choose regions** - GCP region, Supabase region (proximity matters)

### Before Deployment
1. **Complete service modules** - Use template, reference users_service
2. **Update app code** - Secret file reading (critical!)
3. **Build images** - Test locally first
4. **Review tfvars** - Double-check project_id, image URLs

### After Deployment
1. **Test thoroughly** - Don't skip health checks
2. **Monitor costs** - Set budget alerts
3. **Document issues** - Track any problems for hardening phase

---

## 🚀 Next Steps for You

### Step 1: Review (30 mins)
```bash
cd infra-v2

# Read comprehensive guide
cat README.md

# Read bootstrap guide
cat bootstrap/README.md

# Review example service
cat modules/users_service/main.tf

# Review template
cat modules/_TEMPLATE_SERVICE/main.tf.template
```

### Step 2: Customize (15 mins)
```bash
cd bootstrap

# Update naming in all scripts
sed -i 's/MindMirror/Swae/g' *.sh
sed -i 's/mindmirror/swae/g' *.sh

# Review changes
git diff
```

### Step 3: Execute (2 hours)
```bash
# Run bootstrap scripts in order
./00-create-gcp-project.sh
./05-bootstrap-gcp.sh
./01-setup-secrets.sh
./02-setup-supabase.sh
./03-run-migrations.sh
./04-apply-rls-policies.sh
```

### Step 4: Complete Modules (2-3 hours)
```bash
cd ../modules

# For each service:
# 1. Copy template
# 2. Rename files
# 3. Update secrets
# 4. Update variables

# Start with agent_service (most complex)
```

### Step 5: Update Code (1-2 hours)
```bash
cd ../../

# Update Python services
vim src/agent_service/app/config.py
# Add read_secret() function
# Update all secret reads

# Repeat for other services
```

### Step 6: Build & Deploy (2-3 hours)
```bash
# Build images
# Create env.production.tfvars
# Run tofu init/plan/apply
# Update service URLs
# Test everything
```

---

## ✨ Summary

**What we built:**
- Complete production infrastructure (Cloud Run v2)
- Automated bootstrap process (6 scripts)
- Secure secret management (volume mounts)
- Database security (RLS policies)
- Reusable modules (template-based)
- Comprehensive documentation

**What you need to do:**
- Complete 8 service modules (copy from template)
- Update app code for secret files (Python + Node.js)
- Build Docker images
- Run bootstrap scripts
- Deploy infrastructure

**Timeline:**
- MVP: 8-10 hours (EOD if starting now)
- Hardening: 24-48 hours (VPC, gateway auth, CI/CD)

**Ready to start?** Begin with `infra-v2/README.md` 🚀
