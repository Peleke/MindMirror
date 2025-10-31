# Swae Production Infrastructure (infra-v2)

**Status:** ✅ All Modules Complete - Ready for App Code Updates & Deployment
**Last Updated:** 2025-10-20
**Version:** 2.0 (Cloud Run v2 + Secret Volume Mounts)

---

## ✅ **COMPLETION STATUS**

### **What's Done**

All infrastructure code is complete and ready for deployment:

1. ✅ **Bootstrap Scripts** (6 scripts in `bootstrap/`)
   - GCP project creation
   - API enablement & state bucket
   - Secret Manager setup
   - Supabase project creation
   - Database migrations
   - RLS policy application

2. ✅ **OpenTofu Infrastructure** (9 modules)
   - Root module (main.tf, variables.tf, outputs.tf)
   - Base module (service accounts, IAM, GCS)
   - Reusable cloud-run-v2 module
   - 8 service modules (agent, journal, habits, meals, movements, practices, gateway, celery_worker)
   - users_service module (reference implementation)

3. ✅ **Documentation**
   - This README (start here!)
   - STATUS.md (detailed status)
   - MODULES-COMPLETE.md (implementation details)
   - bootstrap/README.md (bootstrap guide)
   - env.production.tfvars.example (configuration template)

**Total Files Created:** 50+ files
**Total Implementation Time:** ~3 hours
**Infrastructure Cost:** ~$50-100/month (alpha period)

---

## 📋 **YOUR TODO LIST - NEXT STEPS**

### **Phase 1: Code Preparation** (2-3 hours)

#### ☐ **1. Review Bootstrap Scripts**
```bash
cd infra-v2/bootstrap

# Customize naming if needed
sed -i 's/MindMirror/Swae/g' *.sh
sed -i 's/mindmirror/swae/g' *.sh

# Review each script
cat 00-create-gcp-project.sh
cat 05-bootstrap-gcp.sh
cat 01-setup-secrets.sh
cat 02-setup-supabase.sh
cat 03-run-migrations.sh
cat 04-apply-rls-policies.sh
```

#### ☐ **2. Update Application Code for Secret Volume Mounts**

**CRITICAL:** Services must read secrets from files, not environment variables.

**Python Services (7 services):**

Add this helper function to each service's config file:

```python
# Add to: src/agent_service/app/config.py
# Add to: src/journal_service/journal_service/config.py
# Add to: habits_service/habits_service/app/config.py
# Add to: meals_service/meals_service/config.py
# Add to: movements_service/movements_service/config.py
# Add to: practices_service/practices/config.py
# Add to: users_service/users_service/config.py

import os
from pathlib import Path

def read_secret(secret_name: str) -> str:
    """Read secret from volume mount or fall back to env var for local dev."""
    secret_path = Path(f"/secrets/{secret_name}/{secret_name}")

    if secret_path.exists():
        return secret_path.read_text().strip()

    # Fallback to env var for local development
    env_var_name = secret_name.upper().replace('-', '_')
    return os.getenv(env_var_name, '')

# Then replace all secret reads:
# OLD: database_url = os.getenv("DATABASE_URL")
# NEW: database_url = read_secret("database-url")
```

**Gateway (Node.js):**

Add this to `mesh/gateway.config.ts`:

```javascript
const fs = require('fs');

function readSecret(secretName) {
  try {
    return fs.readFileSync(`/secrets/${secretName}/${secretName}`, 'utf8').trim();
  } catch (error) {
    // Fallback to env var for local development
    return process.env[secretName.toUpperCase().replace(/-/g, '_')] || '';
  }
}

// Then replace all secret reads:
// OLD: const supabaseJwtSecret = process.env.SUPABASE_JWT_SECRET;
// NEW: const supabaseJwtSecret = readSecret('supabase-jwt-secret');
```

**Secret Name Mapping:**
- `DATABASE_URL` → `read_secret("database-url")`
- `REDIS_URL` → `read_secret("redis-url")`
- `OPENAI_API_KEY` → `read_secret("openai-api-key")`
- `QDRANT_URL` → `read_secret("qdrant-url")`
- `QDRANT_API_KEY` → `read_secret("qdrant-api-key")`
- `SUPABASE_URL` → `read_secret("supabase-url")`
- `SUPABASE_ANON_KEY` → `read_secret("supabase-anon-key")`
- `SUPABASE_SERVICE_ROLE_KEY` → `read_secret("supabase-service-role-key")`
- `SUPABASE_JWT_SECRET` → `read_secret("supabase-jwt-secret")`
- `REINDEX_SECRET_KEY` → `read_secret("reindex-secret-key")`

#### ☐ **3. Build and Push Docker Images**

```bash
# Set project variables
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1

# Agent Service
cd src/agent_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/agent-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/agent-service:latest

# Journal Service
cd ../journal_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/journal-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/journal-service:latest

# Habits Service
cd ../../habits_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/habits-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/habits-service:latest

# Meals Service
cd ../meals_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/meals-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/meals-service:latest

# Movements Service
cd ../movements_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/movements-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/movements-service:latest

# Practices Service
cd ../practices_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/practices-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/practices-service:latest

# Users Service
cd ../users_service
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/users-service:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/users-service:latest

# Gateway
cd ../mesh
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/gateway:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/gateway:latest

# Celery Worker
cd ../celery-worker
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/swae/celery-worker:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/swae/celery-worker:latest
```

#### ☐ **4. Create Production Variables File**

```bash
cd infra-v2

# Copy example
cp env.production.tfvars.example env.production.tfvars

# Edit with your values
vim env.production.tfvars
```

**Required changes in env.production.tfvars:**
- `project_id` - Your GCP project ID
- All `*_image` variables - Update with your Artifact Registry URLs
- Review scaling settings (min_instances, max_instances)
- Review resource limits (cpu_limit, memory_limit)

---

### **Phase 2: Bootstrap & Deploy** (4-6 hours)

#### ☐ **5. Run Bootstrap Scripts**

**Prerequisites:**
- GCP billing account ID
- OpenAI API key
- Qdrant URL + API key
- Redis URL (Upstash or managed Redis)

```bash
cd infra-v2/bootstrap

# 1. Create GCP project (15 mins)
export BILLING_ACCOUNT_ID="YOUR-BILLING-ID"
./00-create-gcp-project.sh

# 2. Bootstrap GCP infrastructure (15 mins)
./05-bootstrap-gcp.sh

# 3. Create secrets (15 mins - interactive)
./01-setup-secrets.sh

# 4. Create Supabase project (30 mins)
./02-setup-supabase.sh

# 5. Run database migrations (15 mins)
./03-run-migrations.sh

# 6. Apply RLS policies (10 mins)
./04-apply-rls-policies.sh
```

**Total bootstrap time:** ~2 hours

#### ☐ **6. Initialize OpenTofu and Deploy Infrastructure**

```bash
cd infra-v2

# Initialize with GCS backend
tofu init -backend-config="bucket=swae-tofu-state"

# Plan deployment (review carefully!)
tofu plan -var-file=env.production.tfvars

# Apply (creates Cloud Run services, Pub/Sub, etc.)
tofu apply -var-file=env.production.tfvars
```

**Deployment time:** 5-10 minutes

#### ☐ **7. Update Service URL Secrets**

After first deployment, service URLs need to be updated:

```bash
# Get deployed URLs
cd infra-v2
GATEWAY_URL=$(tofu output -raw gateway_url)
AGENT_URL=$(tofu output -raw agent_service_url)
JOURNAL_URL=$(tofu output -raw journal_service_url)
HABITS_URL=$(tofu output -raw habits_service_url)
MEALS_URL=$(tofu output -raw meals_service_url)
MOVEMENTS_URL=$(tofu output -raw movements_service_url)
PRACTICES_URL=$(tofu output -raw practices_service_url)
USERS_URL=$(tofu output -raw users_service_url)
CELERY_WORKER_URL=$(tofu output -raw celery_worker_url)

# Update secrets
echo -n "$AGENT_URL" | gcloud secrets versions add AGENT_SERVICE_URL --data-file=-
echo -n "$JOURNAL_URL" | gcloud secrets versions add JOURNAL_SERVICE_URL --data-file=-
echo -n "$HABITS_URL" | gcloud secrets versions add HABITS_SERVICE_URL --data-file=-
echo -n "$MEALS_URL" | gcloud secrets versions add MEALS_SERVICE_URL --data-file=-
echo -n "$CELERY_WORKER_URL" | gcloud secrets versions add CELERY_WORKER_URL --data-file=-

# Redeploy to pick up correct URLs
tofu apply -var-file=env.production.tfvars -auto-approve
```

#### ☐ **8. Validate Production Deployment**

**Health Checks:**
```bash
# Test all service health endpoints
curl -f $AGENT_URL/health
curl -f $JOURNAL_URL/health
curl -f $HABITS_URL/health
curl -f $MEALS_URL/health
curl -f $MOVEMENTS_URL/health
curl -f $PRACTICES_URL/health
curl -f $USERS_URL/health
curl -f $GATEWAY_URL/healthcheck  # Note: different path
curl -f $CELERY_WORKER_URL/health
```

**GraphQL Gateway:**
```bash
# Test GraphQL federation
curl -X POST $GATEWAY_URL/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'
```

**End-to-End Voucher Flow:**
1. Open web app admin UI
2. Create magic link voucher
3. Use magic link to sign up
4. Log a workout
5. Verify data in Supabase dashboard
6. Verify RLS policies prevent cross-user access

---

## 📦 **WHAT WAS BUILT**

### **Service Modules Created**

All modules use Cloud Run v2 with secret volume mounts:

1. **agent_service** - AI conversation engine
   - 8 secrets (database, redis, qdrant, openai, supabase)
   - CRITICAL (min_instances=1)
   - GCS integration, LangGraph orchestration

2. **journal_service** - Structured journaling
   - 7 secrets (database, redis, supabase, reindex key)
   - Automatic Qdrant indexing
   - GCS integration

3. **habits_service** - Habit tracking
   - 1 secret (database)
   - DB pool configuration
   - Program template IDs

4. **meals_service** - Meal logging
   - 1 secret (database)
   - Open Food Facts API integration

5. **movements_service** - Exercise tracking
   - 1 secret (database)
   - ExerciseDB API integration
   - DB pool configuration

6. **practices_service** - Workout programs
   - 1 secret (database)
   - Users service integration

7. **gateway** - GraphQL Hive federation
   - 2 secrets (supabase anon key, JWT secret)
   - CRITICAL (min_instances=1)
   - Federates all 7 microservices
   - Port 4000, health check: `/healthcheck`

8. **celery_worker** - Background tasks
   - 6 secrets (database, redis, qdrant, openai, reindex)
   - 5 Pub/Sub topics + subscriptions
   - Push subscriptions with OIDC auth, DLQ, retries
   - Own service account with pubsub permissions

9. **users_service** - User profiles
   - 1 secret (database)
   - CRITICAL (min_instances=1)
   - Central hub (entire system depends on it)

### **Infrastructure Components**

- **Base Module:** Service accounts, IAM bindings, GCS bucket
- **Reusable Cloud Run v2 Module:** Secret volumes, health checks, scaling
- **Pub/Sub:** 5 topics, 5 subscriptions (for Celery worker)
- **Service Accounts:** One per service with least-privilege IAM
- **Secret Manager:** All credentials stored securely
- **GCS:** State bucket + traditions bucket

---

## 🔐 **KEY FEATURES**

### **Security Improvements**

✅ **Secret Volume Mounts** (not environment variables)
- Secrets mounted as files: `/secrets/<volume-name>/<filename>`
- Not visible in logs, env vars, or crash dumps
- Supports secret rotation without redeployment

✅ **Row-Level Security (RLS)**
- Database-level user isolation
- 6 tables protected (vouchers, journals, habits, practices, meals, movements)
- Service role bypass for admin operations

✅ **Least-Privilege IAM**
- Each service has dedicated service account
- IAM roles scoped to specific resources
- No project-wide permissions

### **Performance Improvements**

✅ **Cloud Run v2** (not deprecated v1)
- Modern platform features
- Better cold start performance
- Improved health check system

✅ **Min Instances for Critical Services**
- agent_service: min_instances=1
- gateway: min_instances=1
- users_service: min_instances=1
- **Result:** Zero cold starts for user-facing requests

✅ **Health Checks**
- Startup probes (gives service time to boot)
- Liveness probes (monitors ongoing health)
- Configurable timeouts and thresholds

### **Developer Experience**

✅ **Reusable Modules**
- cloud-run-v2 module used by all services
- Consistent structure across all modules
- Easy to add new services

✅ **Comprehensive Documentation**
- README.md (this file)
- STATUS.md (detailed status)
- MODULES-COMPLETE.md (implementation guide)
- bootstrap/README.md (bootstrap instructions)

✅ **Example Configuration**
- env.production.tfvars.example
- Copy, customize, deploy

---

## 📊 **ARCHITECTURE OVERVIEW**

### **Service Dependencies**

```
Gateway (Port 4000)
├─→ Agent Service (Port 8000)
├─→ Journal Service (Port 8000)
├─→ Habits Service (Port 8003)
├─→ Meals Service (Port 8000)
├─→ Movements Service (Port 8000)
├─→ Practices Service (Port 8000)
└─→ Users Service (Port 8000) ← CRITICAL PATH

Celery Worker (Port 8000)
├─→ Journal Service
└─→ Agent Service

Journal Service
├─→ Agent Service
├─→ Celery Worker
└─→ Users Service

Practices Service
└─→ Users Service
```

### **Secret Distribution**

- **Most secrets:** agent_service (8)
- **Fewest secrets:** habits, meals, movements, practices (1 each)
- **Gateway secrets:** 2 (supabase anon key, JWT secret)
- **Celery worker secrets:** 6 (similar to agent)

### **Deployment Order**

1. Base infrastructure (service accounts, GCS)
2. Users service (everything depends on it)
3. Core services (agent, journal, habits, meals, movements, practices)
4. Celery worker (background tasks)
5. Gateway (user-facing, deploy last)

---

## 🔧 **COMMON TASKS**

### **View Service Logs**

```bash
gcloud run services logs read SERVICE_NAME --region=$REGION --limit=100
```

### **Update a Service**

```bash
# Make changes to module
vim modules/agent_service/main.tf

# Plan
tofu plan -var-file=env.production.tfvars

# Apply
tofu apply -var-file=env.production.tfvars
```

### **Scale a Service**

Edit `env.production.tfvars`:
```hcl
min_instances_critical = 2  # Was 1
```

Apply:
```bash
tofu apply -var-file=env.production.tfvars
```

### **Add a Secret to a Service**

1. Create secret in Secret Manager
2. Add to module's `secret_volumes` list
3. Add variable to `variables.tf`
4. Pass from parent module
5. Update app code to read from file
6. Deploy

---

## 🚨 **TROUBLESHOOTING**

### **Service Won't Start**

**Check logs:**
```bash
gcloud run services logs read SERVICE_NAME --region=$REGION --limit=50
```

**Common issues:**
- Secret not mounted → Check service account has `secretmanager.secretAccessor`
- Health check failing → Verify `/health` endpoint returns 200
- App can't read secret → Check path: `/secrets/<volume-name>/<filename>`

### **Database Connection Fails**

**Test connection:**
```bash
DATABASE_URL=$(gcloud secrets versions access latest --secret="DATABASE_URL")
psql "$DATABASE_URL" -c "SELECT 1"
```

**Common issues:**
- Wrong DATABASE_URL format
- Supabase IP allowlist blocking Cloud Run
- SSL certificate issues

### **Circular Dependency Error**

This is expected on first deployment (service URLs are placeholders).

**Solution:**
1. Deploy with placeholders
2. Update service URL secrets with real URLs (step 7 above)
3. Redeploy

---

## 💰 **COST ESTIMATES**

**Alpha period (3-10 users):** ~$50-100/month

**Breakdown:**
- Cloud Run (3 min instances) = ~$52/month
- Cloud Run (requests) = ~$5/month
- Secret Manager = ~$1/month
- GCS = ~$1/month
- Pub/Sub = ~$1/month

**Set budget alert:**
```bash
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT_ID \
  --display-name="Swae Production" \
  --budget-amount=100USD \
  --threshold-rule=percent=90
```

---

## 📚 **ADDITIONAL DOCUMENTATION**

- **STATUS.md** - Current status and what's next
- **MODULES-COMPLETE.md** - Detailed module implementation guide
- **bootstrap/README.md** - Bootstrap script documentation
- **env.production.tfvars.example** - Configuration template
- **../docs/PRODUCTION-DEPLOYMENT-RUNBOOK.md** - End-to-end deployment guide
- **../docs/epics/epic-3-infrastructure.md** - Infrastructure epic

---

## 🎯 **SUCCESS CRITERIA**

Production deployment is successful when:

- [x] All 8 service modules created
- [ ] App code updated to read secrets from files
- [ ] All 9 Docker images built and pushed
- [ ] Bootstrap scripts executed successfully
- [ ] Infrastructure deployed via OpenTofu
- [ ] All service health checks pass
- [ ] Gateway federates all microservice schemas
- [ ] End-to-end voucher flow works
- [ ] RLS policies prevent cross-user data access
- [ ] Costs under $100/month projected

---

## ⏱️ **ESTIMATED TIMELINE**

**Total:** 6-8 hours (from current state to production)

- ✅ Infrastructure code: **DONE** (3 hours)
- ☐ App code updates: 1-2 hours
- ☐ Docker builds: 1 hour
- ☐ Bootstrap: 2 hours
- ☐ Deployment: 1 hour
- ☐ Validation: 1 hour

---

## 🚀 **QUICK START**

```bash
# 1. Review this README (you are here!)

# 2. Update app code for secret volumes
cd ../src/agent_service/app
vim config.py  # Add read_secret() function

# 3. Build images
cd ../../infra-v2
# Follow "Build and Push Docker Images" section above

# 4. Run bootstrap
cd bootstrap
./00-create-gcp-project.sh
./05-bootstrap-gcp.sh
./01-setup-secrets.sh
./02-setup-supabase.sh
./03-run-migrations.sh
./04-apply-rls-policies.sh

# 5. Deploy
cd ..
cp env.production.tfvars.example env.production.tfvars
vim env.production.tfvars
tofu init -backend-config="bucket=swae-tofu-state"
tofu plan -var-file=env.production.tfvars
tofu apply -var-file=env.production.tfvars

# 6. Update service URLs and redeploy
# Follow "Update Service URL Secrets" section above

# 7. Validate
# Follow "Validate Production Deployment" section above
```

---

## ✅ **DONE - READY TO PROCEED**

All infrastructure code is complete. The path forward is clear:

1. Update app code for secret files
2. Build Docker images
3. Run bootstrap scripts
4. Deploy infrastructure
5. Test and validate

**You've got this!** 🚀

---

**Questions?** Review the documentation or check specific modules for implementation details.
