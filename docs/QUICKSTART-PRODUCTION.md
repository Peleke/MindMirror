# Production Deployment Quick Start
**Goal**: Get MindMirror running in production in 2 weeks
**Target**: End users by mid-November 2025

---

## Prerequisites

### Required Accounts
- ✅ GCP project with billing enabled
- ✅ GitHub repository with Actions enabled
- ✅ Qdrant Cloud account (vector database)

### Required Tools
```bash
# Install required CLI tools
curl -sSL https://rover.apollo.dev/nix/latest | sh  # Rover (GraphQL)
curl https://sdk.cloud.google.com | bash            # gcloud CLI

# Verify installations
rover --version
gcloud --version
```

### Repository Secrets
Configure in GitHub → Settings → Secrets and variables → Actions:

```
GCP_PROJECT_ID          # Your GCP project ID
GCP_SERVICE_ACCOUNT_KEY # JSON key for github-actions@PROJECT.iam.gserviceaccount.com
```

---

## Week 1: Bootstrap Infrastructure

### Day 1-2: GCP Setup

**1. Create GCP Service Account for GitHub Actions**
```bash
# Set project
export PROJECT_ID="mindmirror-prod"
gcloud config set project $PROJECT_ID

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions CI/CD"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Add to GitHub secrets (copy contents of github-actions-key.json)
cat github-actions-key.json
# → Paste into GitHub secret GCP_SERVICE_ACCOUNT_KEY

# Clean up local key
rm github-actions-key.json
```

**2. Enable Required APIs**
```bash
cd infra-v2/bootstrap
chmod +x 02-enable-apis.sh
./02-enable-apis.sh

# OR manually:
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudresourcemanager.googleapis.com
```

**3. Create Artifact Registry**
```bash
chmod +x 03-create-artifact-registry.sh
./03-create-artifact-registry.sh

# OR manually:
gcloud artifacts repositories create services \
  --repository-format=docker \
  --location=us-central1 \
  --description="MindMirror service containers"
```

**4. Create Secrets in Secret Manager**
```bash
# Already created ✅ (via 01-setup-secrets.sh)
# Verify:
gcloud secrets list
```

### Day 3-4: Docker Standardization

**1. Verify All Dockerfiles Use Habits Pattern**
```bash
# Check all Dockerfiles exist
for service in meals movements practices users; do
  if [ ! -f "${service}_service/Dockerfile" ]; then
    echo "Missing Dockerfile for ${service}_service"
  fi
done

# Test local builds
docker compose build

# Verify no errors
```

**If Dockerfiles need updates, see** `docs/devops-strategy.md` for standard template.

### Day 5-7: First Deployment

**1. Push to Main (Triggers Auto-Deploy)**
```bash
# Ensure all changes committed
git add .
git commit -m "feat: initial production setup"
git push origin main

# Monitor GitHub Actions
# → Go to repository → Actions tab
# → Watch CI/CD workflow
```

**2. Verify Deployment**
```bash
# Wait for GitHub Actions to complete (5-10 minutes)

# Check deployed services
gcloud run services list --region=us-central1

# Run health checks
chmod +x scripts/health-check-all.sh
./scripts/health-check-all.sh production
```

---

## Week 2: Database & Gateway Setup

### Day 8-9: Database Migrations

**1. Deploy Cloud SQL (if not done via OpenTofu)**
```bash
# Option A: Manual (quick)
gcloud sql instances create mindmirror-main \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=us-central1 \
  --network=default

# Create databases
gcloud sql databases create agent --instance=mindmirror-main
gcloud sql databases create journal --instance=mindmirror-main
gcloud sql databases create habits --instance=mindmirror-main

# Option B: OpenTofu (recommended for prod)
cd infra-v2/environments/production
tofu init
tofu plan -out=tfplan
tofu apply tfplan
```

**2. Run Migrations**
```bash
# Via Cloud Run Job (if created by infra-v2)
gcloud run jobs execute migrate-main --region=us-central1 --wait

# OR manually via local connection
# (Use Cloud SQL Proxy for secure connection)
cloud_sql_proxy -instances=mindmirror-prod:us-central1:mindmirror-main=tcp:5432 &

# Run Alembic
cd src/alembic-config
poetry run alembic upgrade head
```

### Day 10-11: GraphQL Gateway Setup

**1. Install Rover (if not done)**
```bash
curl -sSL https://rover.apollo.dev/nix/latest | sh
source ~/.bashrc
```

**2. Create GCS Bucket for Supergraph**
```bash
gsutil mb -p $PROJECT_ID -l us-central1 gs://mindmirror-prod-mesh
```

**3. Update Gateway (Manual - Phase 1)**
```bash
# Set environment variables
export GCP_PROJECT_ID="mindmirror-prod"
export GCP_REGION="us-central1"
export MESH_BUCKET="mindmirror-prod-mesh"

# Run gateway update script
chmod +x scripts/update-gateway.sh
./scripts/update-gateway.sh all
```

**Expected Output**:
```
[INFO] Introspecting agent_service at https://agent-service-...
[INFO] ✓ Successfully introspected agent_service
...
[INFO] Composing supergraph from subgraphs
[INFO] ✓ Supergraph composed successfully
[INFO] Uploading supergraph to GCS
[INFO] ✓ Updated gs://mindmirror-prod-mesh/supergraph-latest.graphql
[INFO] Deploying mesh gateway with new supergraph
[INFO] ✓ Gateway deployed successfully
[INFO] ✓ Gateway is healthy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gateway update complete! 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Day 12-14: Launch & Verify

**1. Final Health Check**
```bash
./scripts/health-check-all.sh production
```

**Expected Output**:
```
[INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[INFO] Health Check: production environment
[INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[INFO] ━━━ Checking agent-service ━━━
[INFO] ✓ agent-service is healthy (HTTP 200)
[INFO] ✓ agent-service GraphQL endpoint is healthy
...
[INFO] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[INFO] ✓ All services healthy (9/9)
[INFO] Production is ready! 🚀
```

**2. Test GraphQL Gateway**
```bash
# Get gateway URL
GATEWAY_URL=$(gcloud run services describe mesh-gateway \
  --region=us-central1 \
  --format='value(status.url)')

echo "Gateway URL: $GATEWAY_URL/graphql"

# Test with curl
curl -X POST $GATEWAY_URL/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'
```

**3. Invite Beta Users**
```bash
# Share URL with first 5 users
echo "Production URL: $GATEWAY_URL"
```

---

## Daily Operations

### Deploy Code Changes
```bash
# 1. Make changes on feature branch
git checkout -b feature/new-thing

# 2. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/new-thing

# 3. Create PR (triggers CI tests)
gh pr create

# 4. Merge to main (triggers auto-deploy)
gh pr merge --squash

# 5. Monitor deployment in GitHub Actions
# → Services deploy automatically in ~5 minutes
```

### Update Gateway (When Schema Changes)
```bash
# IF you changed GraphQL schemas (*.graphql files):
./scripts/update-gateway.sh <service_name>

# Example:
./scripts/update-gateway.sh habits_service

# OR update all services:
./scripts/update-gateway.sh all
```

### View Logs
```bash
# All services
gcloud logging tail "resource.type=cloud_run_revision" --format=json

# Specific service
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service"

# Errors only
gcloud logging tail "resource.type=cloud_run_revision AND severity>=ERROR"
```

### Rollback Service
```bash
# List revisions
gcloud run revisions list --service=agent-service --region=us-central1

# Rollback to specific revision
gcloud run services update-traffic agent-service \
  --to-revisions agent-service-00042-abc=100 \
  --region=us-central1
```

---

## Troubleshooting

### Service Won't Deploy
```bash
# Check build logs in GitHub Actions
# → Actions tab → Latest workflow run

# Check Cloud Run logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=<SERVICE>"

# Common issues:
# 1. Missing secrets → Check Secret Manager
# 2. Database connection → Verify Cloud SQL is running
# 3. Port mismatch → Check Dockerfile EXPOSE vs Cloud Run --port
```

### Gateway Returns Errors
```bash
# 1. Verify all services are healthy
./scripts/health-check-all.sh

# 2. Check supergraph composition
rover supergraph check --schema /tmp/supergraph.graphql

# 3. Re-run gateway update
./scripts/update-gateway.sh all

# 4. Check gateway logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=mesh-gateway"
```

### Database Connection Issues
```bash
# Verify Cloud SQL is running
gcloud sql instances list

# Check connection from Cloud Run
gcloud run services describe agent-service --region=us-central1

# Verify secret exists
gcloud secrets versions access latest --secret=database-url
```

---

## Success Checklist

### Week 1 Complete
- [ ] GCP project configured
- [ ] GitHub secrets configured
- [ ] All services deployed to Cloud Run
- [ ] Health checks passing

### Week 2 Complete
- [ ] Cloud SQL databases running
- [ ] Alembic migrations applied
- [ ] GraphQL gateway federating all services
- [ ] 5 beta users invited
- [ ] No critical errors in logs

### Ready for Scale
- [ ] All services auto-deploying on merge to main
- [ ] Manual gateway update working
- [ ] Health check script working
- [ ] Rollback procedure tested
- [ ] Logging accessible

---

## Next Steps (Phase 2)

After production is stable (2-4 weeks), implement automation:

1. **Automated Gateway Updates** (Dec)
   - Detect schema changes in CI
   - Auto-compose and deploy supergraph
   - Block PRs with invalid schemas

2. **Terrateam Integration** (Jan)
   - PR-driven infrastructure changes
   - Approval gates for production
   - Automated rollbacks

3. **Observability** (Feb)
   - Custom dashboards
   - Alerting on errors
   - Distributed tracing

See `docs/devops-phased-plan.md` for full Phase 2 details.

---

## Support

**Runbooks**:
- `docs/devops-strategy.md` - Full DevOps strategy
- `docs/devops-phased-plan.md` - Phased implementation plan

**Scripts**:
- `scripts/update-gateway.sh` - Manual gateway update
- `scripts/health-check-all.sh` - Health check all services
- `scripts/changed-services.sh` - Detect changed services (CI)

**Workflows**:
- `.github/workflows/ci-build-deploy.yml` - Build and deploy on merge

---

**Let's ship this.** 🚀
