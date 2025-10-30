# MindMirror DevOps: Phased Deployment Plan
**Target**: Production live by **end of 2025** (2 months)
**Philosophy**: Ship fast, automate incrementally, users ASAP

---

## Timeline Overview

```
NOW ─────────────► DEC 24 ────────► JAN 15 ────────► FEB 28
│                  │               │                │
Phase 1:           Phase 1         Phase 2          Phase 2
MVP Deploy         Complete        Mid              Complete
(Week 1-2)         (4 weeks)       (2 weeks)        (4 weeks)
│                  │               │                │
Manual ops         Users live!     Automation       Polished
Basic CI/CD        Basic monitor   GraphQL auto     App stores
```

**Critical Path**:
- **Week 1-2** (Nov 1-15): Phase 1 setup → production deployed
- **Week 3-4** (Nov 16-30): First real users → iterate on bugs
- **Dec 1-24**: Phase 2 automation → reduce manual toil
- **Jan-Feb**: Polish, app store submission, scale testing

---

## Phase 1: MVP Deploy (Manual Gateway, Basic CI/CD)
**Goal**: Get production running with MANUAL gateway updates, automated service deploys
**Timeline**: 2 weeks
**User Impact**: Real users can start using the app

### What We Build

#### 1. Infrastructure (OpenTofu)
- ✅ Cloud Run services (all 8 services)
- ✅ Cloud SQL databases (4 instances)
- ✅ Secret Manager integration
- ✅ Artifact Registry
- ❌ **Skip**: Complex networking, autoscaling tuning, observability dashboards

#### 2. CI/CD (GitHub Actions)
- ✅ Build & push Docker images on merge to `main`
- ✅ Auto-deploy services to Cloud Run (via gcloud CLI, NOT Terrateam yet)
- ✅ Health checks after deploy
- ❌ **Skip**: Terrateam integration, sophisticated rollback, canary deploys

#### 3. Gateway/Mesh Handling
- ✅ **MANUAL** gateway updates when schemas change
- ✅ Simple runbook: "Schema changed? Run these 3 commands"
- ❌ **Skip**: Automated rover composition, PR-driven supergraph updates

#### 4. Database Migrations
- ✅ Manual Alembic runs via Cloud Run Job (triggered by script)
- ✅ Health check confirms migration success
- ❌ **Skip**: Automated migration in CI/CD pipeline

### Workflow in Phase 1

**Developer Flow**:
```bash
# 1. Make code changes
git checkout -b feature/new-thing
# ... edit code

# 2. Push to branch (CI runs tests only)
git push origin feature/new-thing

# 3. Merge to main (CI builds + deploys automatically)
gh pr merge --squash

# 4. IF schema changed → MANUAL gateway update
scripts/update-gateway.sh habits_service
# (script introspects, composes, redeploys mesh)
```

**Gateway Update (Manual)**:
```bash
#!/usr/bin/env bash
# scripts/update-gateway.sh habits_service

# 1. Introspect changed service
rover subgraph introspect https://habits-service-prod.run.app/graphql > habits.graphql

# 2. Update supergraph config
cat > supergraph-config.yaml <<EOF
subgraphs:
  - name: habits
    routing_url: https://habits-service-prod.run.app/graphql
    schema: ./habits.graphql
  # ... paste other services
EOF

# 3. Compose supergraph
rover supergraph compose --config supergraph-config.yaml > supergraph.graphql

# 4. Upload to GCS
gsutil cp supergraph.graphql gs://mindmirror-prod-mesh/supergraph-$(date +%s).graphql
gsutil cp supergraph.graphql gs://mindmirror-prod-mesh/supergraph-latest.graphql

# 5. Redeploy mesh (reads from GCS)
gcloud run deploy mesh-gateway --image=us-central1-docker.pkg.dev/.../mesh:latest --region=us-central1
```

**Trade-off**:
- ✅ Get to production in 2 weeks
- ✅ Schema changes are RARE (not every deploy)
- ⚠️ Manual step required when schemas change (acceptable for Phase 1)
- ⚠️ Forget to update gateway → API errors (mitigated by runbook + alerts)

---

## Phase 2: Automation (Rover, Terrateam, Full CI/CD)
**Goal**: Eliminate manual toil, production-grade automation
**Timeline**: 6 weeks (Dec-Feb)
**User Impact**: Faster iteration, fewer human errors

### What We Build

#### 1. Automated Gateway Composition
- ✅ Detect schema changes in CI
- ✅ Auto-run rover introspect + compose
- ✅ Auto-deploy mesh with new supergraph
- ✅ Block PR if composition fails

#### 2. Terrateam Integration
- ✅ PR-driven Terraform plans
- ✅ Approval gates for production
- ✅ Automated variable injection (image tags)

#### 3. Database Migration Automation
- ✅ Auto-run Alembic before service deploy
- ✅ Rollback on migration failure

#### 4. Observability
- ✅ Custom Cloud Monitoring dashboards
- ✅ Alerting (error rate, latency)
- ✅ Log-based metrics

#### 5. Rollback & Recovery
- ✅ One-click rollback to previous revision
- ✅ Automated rollback on health check failure

### Workflow in Phase 2

**Developer Flow** (fully automated):
```bash
# 1. Make code changes (including schema changes)
git checkout -b feature/new-thing
# ... edit code, modify GraphQL schema

# 2. Push → PR opened
git push origin feature/new-thing
gh pr create

# CI automatically:
# - Runs tests
# - Builds images
# - Detects schema changes
# - Composes supergraph (or fails PR if invalid)
# - Posts Terrateam plan in PR comments

# 3. Review plan → merge
gh pr merge --squash

# CI automatically:
# - Pushes images
# - Runs migrations
# - Deploys services
# - Composes + deploys gateway
# - Verifies health checks
# - Rolls back on failure
```

**Trade-off**:
- ✅ Zero manual steps
- ✅ Safer (composition validated in PR)
- ⚠️ Requires 4-6 weeks to build properly
- ⚠️ Not needed for initial launch

---

## The Boundary: What's Manual vs Automated

| Task | Phase 1 (Manual) | Phase 2 (Auto) |
|------|------------------|----------------|
| **Build Docker images** | ✅ Auto (GH Actions) | ✅ Auto |
| **Deploy services** | ✅ Auto (gcloud CLI) | ✅ Auto (Terrateam) |
| **Update gateway** | ❌ Manual script | ✅ Auto (rover + CI) |
| **Run migrations** | ❌ Manual script | ✅ Auto (pre-deploy) |
| **Rollback** | ❌ Manual (gcloud) | ✅ Auto (on failure) |
| **Terraform apply** | ❌ Manual (tofu apply) | ✅ Auto (Terrateam) |
| **Schema validation** | ⚠️ Manual (rover local) | ✅ Auto (PR check) |

### Why This Split?

**Phase 1 focuses on**:
- Services deploy automatically (90% of changes)
- Gateway updates are RARE (schema changes every few weeks, not daily)
- Database migrations are INFREQUENT (not every deploy)
- Manual ops are acceptable for low-frequency tasks

**Phase 2 automates**:
- The rare-but-painful manual steps
- Error-prone workflows (schema composition)
- Safety nets (rollbacks, migration failures)

---

## Detailed Phase 1 Implementation

### Week 1: Bootstrap Production

**Day 1-2: Infrastructure**
```bash
# 1. Bootstrap GCP project
cd infra-v2/bootstrap
./02-enable-apis.sh
./03-create-artifact-registry.sh
./01-setup-secrets.sh  # Already done ✅

# 2. Deploy infrastructure
cd infra-v2/environments/production
tofu init
tofu plan -out=tfplan
tofu apply tfplan
# → Creates: Cloud Run services, Cloud SQL, networking
```

**Day 3-4: Docker Standardization**
```bash
# Standardize all Dockerfiles (copy habits pattern)
for service in meals movements practices users; do
  cp habits_service/Dockerfile ${service}_service/Dockerfile
  # Edit paths/ports to match service
done

# Test builds locally
docker compose build
```

**Day 5-7: CI/CD Setup**
```bash
# 1. Create GitHub Actions workflows
.github/workflows/
├── ci-test.yml           # Run tests on PRs
├── ci-build-deploy.yml   # Build + deploy on merge to main

# 2. Configure GitHub secrets
# GCP_PROJECT_ID, GCP_SA_KEY, ARTIFACT_REGISTRY_URL

# 3. First automated deployment
git push origin main  # Triggers build + deploy
```

### Week 2: First Users

**Day 8-9: Database Setup**
```bash
# 1. Run migrations manually (Cloud Run Job)
gcloud run jobs execute migrate-main --region=us-central1 --wait

# 2. Seed initial data (if needed)
# 3. Verify all services healthy
scripts/health-check-all.sh
```

**Day 10-11: Gateway Setup (Manual)**
```bash
# 1. Introspect all services
for svc in agent journal habits meals movements practices users; do
  rover subgraph introspect https://${svc}-service-prod.run.app/graphql > ${svc}.graphql
done

# 2. Compose supergraph
cat > supergraph-config.yaml <<EOF
subgraphs:
  - name: agent
    routing_url: https://agent-service-prod.run.app/graphql
    schema: ./agent.graphql
  # ... all services
EOF

rover supergraph compose --config supergraph-config.yaml > supergraph.graphql

# 3. Upload to GCS
gsutil cp supergraph.graphql gs://mindmirror-prod-mesh/supergraph-latest.graphql

# 4. Deploy mesh
gcloud run deploy mesh-gateway \
  --image=us-central1-docker.pkg.dev/.../mesh:latest \
  --set-env-vars SUPERGRAPH_URL=gs://mindmirror-prod-mesh/supergraph-latest.graphql \
  --region=us-central1
```

**Day 12-14: Launch**
```bash
# 1. Frontend deployment
cd web && npm run build
gcloud run deploy web-app --source . --region=us-central1

# 2. Smoke tests
scripts/smoke-test.sh

# 3. Invite first users
# 4. Monitor logs/errors
gcloud logging tail "resource.type=cloud_run_revision" --format=json
```

### Phase 1 Deliverables

**Code**:
- ✅ `.github/workflows/ci-build-deploy.yml`
- ✅ `scripts/update-gateway.sh` (manual gateway update)
- ✅ `scripts/health-check-all.sh`
- ✅ `infra-v2/environments/production/` (OpenTofu)
- ✅ Standardized Dockerfiles (all services)

**Infrastructure**:
- ✅ Cloud Run: 8 services + mesh + web
- ✅ Cloud SQL: 4 databases
- ✅ Artifact Registry: Container images
- ✅ Secret Manager: All secrets

**Documentation**:
- ✅ Runbook: Manual gateway update
- ✅ Runbook: Manual migration
- ✅ Runbook: Rollback procedure
- ✅ Monitoring guide (Cloud Logging basics)

---

## Detailed Phase 2 Implementation

### December: Automated Gateway

**Week 1: Rover CI Integration**
```yaml
# .github/workflows/graphql-compose.yml
name: GraphQL Composition

on:
  pull_request:
    paths: ['**/*.graphql', '**/schema.py', '**/resolvers.py']

jobs:
  compose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Detect schema changes
        id: detect
        run: scripts/detect-schema-changes.sh

      - name: Introspect changed services (local)
        run: |
          # Start service locally, introspect
          docker compose up -d ${{ steps.detect.outputs.services }}
          sleep 10
          for svc in ${{ steps.detect.outputs.services }}; do
            rover subgraph introspect http://localhost:${PORT}/graphql > ${svc}.graphql
          done

      - name: Compose supergraph
        run: |
          # Generate supergraph-config.yaml dynamically
          scripts/generate-supergraph-config.sh
          rover supergraph compose --config supergraph-config.yaml > supergraph.graphql

      - name: Validate composition
        run: |
          # Fail PR if composition fails
          if ! rover supergraph check --schema supergraph.graphql; then
            echo "❌ Supergraph composition failed! Fix schema conflicts."
            exit 1
          fi

      - name: Upload supergraph artifact
        uses: actions/upload-artifact@v3
        with:
          name: supergraph
          path: supergraph.graphql
```

**Week 2: Auto-Deploy Gateway**
```yaml
# .github/workflows/ci-build-deploy.yml (updated)
deploy-gateway:
  needs: [build-services, compose-supergraph]
  runs-on: ubuntu-latest
  steps:
    - name: Download supergraph
      uses: actions/download-artifact@v3
      with:
        name: supergraph

    - name: Upload to GCS
      run: |
        gsutil cp supergraph.graphql gs://mindmirror-prod-mesh/supergraph-${{ github.sha }}.graphql
        gsutil cp supergraph.graphql gs://mindmirror-prod-mesh/supergraph-latest.graphql

    - name: Deploy mesh
      run: |
        gcloud run deploy mesh-gateway \
          --image=us-central1-docker.pkg.dev/.../mesh:${{ github.sha }} \
          --set-env-vars SUPERGRAPH_URL=gs://mindmirror-prod-mesh/supergraph-latest.graphql \
          --region=us-central1
```

### January: Terrateam + Migrations

**Week 1: Terrateam Setup**
```yaml
# .terrateam/config.yml
workflows:
  plan:
    - type: init
    - type: plan
      extra_args: ["-var", "image_tag=${{ github.sha }}"]

  apply:
    - type: init
    - type: apply
      extra_args: ["-var", "image_tag=${{ github.sha }}"]

environments:
  production:
    path: infra-v2/environments/production
    auto_apply: false  # Require manual approval

  staging:
    path: infra-v2/environments/staging
    auto_apply: true   # Auto-apply on merge
```

**Week 2: Migration Automation**
```yaml
# .github/workflows/run-migrations.yml
run-migrations:
  runs-on: ubuntu-latest
  steps:
    - name: Execute migration job
      run: |
        gcloud run jobs execute migrate-main --region=us-central1 --wait

    - name: Check migration success
      run: |
        # Query job execution status
        status=$(gcloud run jobs executions list --job=migrate-main --limit=1 --format='value(status.conditions[0].type)')
        if [ "$status" != "Completed" ]; then
          echo "❌ Migration failed! Rolling back..."
          # Rollback logic
          exit 1
        fi
```

### February: Observability + Polish

**Week 1: Dashboards**
```bash
# Create Cloud Monitoring dashboard via Terraform
resource "google_monitoring_dashboard" "mindmirror" {
  dashboard_json = file("${path.module}/dashboards/main.json")
}

# Dashboard includes:
# - Request rate per service
# - Error rate (5xx)
# - Latency p50/p95/p99
# - CPU/memory utilization
```

**Week 2: Alerting**
```hcl
resource "google_monitoring_alert_policy" "error_rate" {
  display_name = "High Error Rate"
  conditions {
    display_name = "Error rate > 5%"
    condition_threshold {
      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
      comparison = "COMPARISON_GT"
      threshold_value = 0.05
      duration = "60s"
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.id]
}
```

---

## Risk Mitigation

### Phase 1 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Forget gateway update | 🔴 API breaks | Runbook checklist, alerts on schema mismatch |
| Migration fails | 🔴 App down | Manual rollback procedure, database backups |
| Service crash loop | 🟡 Service down | Health checks, manual rollback |
| Cost overrun | 🟡 Budget exceeded | Budget alerts, right-sizing |

### Phase 2 Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| CI/CD breaks | 🔴 Can't deploy | Fallback to manual deploy, canary rollout |
| Automated rollback fails | 🔴 Bad deploy stuck | Manual intervention runbook |
| Complex debugging | 🟡 Slow iteration | Comprehensive logging, distributed tracing |

---

## Success Metrics

### Phase 1 (Week 2)
- [ ] All 8 services deployed to Cloud Run
- [ ] GraphQL gateway federating all services
- [ ] Web app accessible via public URL
- [ ] 5 beta users using the app
- [ ] No production incidents >30min

### Phase 2 (Feb 28)
- [ ] Zero manual gateway updates required
- [ ] Automated rollback working (tested)
- [ ] App store builds (iOS + Android)
- [ ] 50+ active users
- [ ] <1% error rate sustained

---

## Weekly Cadence (Nov-Dec)

**Every Monday**:
- Review last week's incidents
- Prioritize this week's automation tasks
- Update runbooks

**Every Friday**:
- Deploy window (merge to main)
- Smoke test production
- Monitor over weekend

---

## Critical Path Items (Cannot Slip)

1. **Week 1**: Docker standardization ✅
2. **Week 2**: First production deploy ✅
3. **Week 4**: Beta users live ✅
4. **Dec 24**: Gateway automation complete
5. **Jan 31**: Terrateam + migrations complete
6. **Feb 28**: App store submission

---

## What We're NOT Building (Out of Scope)

### Phase 1
- ❌ Blue/green deployments
- ❌ Canary releases
- ❌ Custom monitoring dashboards
- ❌ Automated security scanning
- ❌ Load testing
- ❌ Multi-region deployment
- ❌ Disaster recovery drills

### Phase 2
- ❌ Custom CI/CD platform (use GitHub Actions)
- ❌ Service mesh (Istio, Linkerd)
- ❌ Advanced autoscaling policies
- ❌ Cost optimization tooling
- ❌ Developer portal

**Why**: These add complexity without user value in first 2 months. Revisit in Q1 2026.

---

## Decision Log

**Manual Gateway Updates (Phase 1)**:
- ✅ Decision: Manual script for gateway updates
- Rationale: Schema changes are rare (<1/week), automation takes 2-3 weeks
- Review: Automate in Phase 2 once production is stable

**Skip Terrateam in Phase 1**:
- ✅ Decision: Use `gcloud` CLI for deploys, add Terrateam in Phase 2
- Rationale: Faster to production, Terrateam integration requires 1-2 weeks
- Review: Add Terrateam once we have 2-3 weeks of production stability

**Manual Migrations**:
- ✅ Decision: Run Alembic manually via script
- Rationale: Migrations are infrequent, automation adds complexity
- Review: Automate in Phase 2 when migration cadence increases

---

## Next Actions (This Week)

1. **Review this plan** → Confirm phasing and boundaries
2. **Create scripts** → `update-gateway.sh`, `health-check-all.sh`
3. **Standardize Dockerfiles** → Apply habits pattern to all services
4. **Bootstrap infrastructure** → Run OpenTofu for production
5. **Create minimal CI/CD** → `.github/workflows/ci-build-deploy.yml`

---

**Let's ship this thing.** 🚀
