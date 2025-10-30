# Epic: Gateway Rebuild Automation

**Epic ID**: `epic-gateway-rebuild-automation`
**Status**: 🔄 In Progress
**Priority**: CRITICAL
**Target Completion**: 2025-10-29 EOD
**Owner**: DevOps/Infrastructure

---

## Problem Statement

The GraphQL Gateway (Hive Gateway) requires service URLs at **BUILD TIME** to generate the federated schema configuration (`mesh.config.dynamic.ts`). Currently, the gateway is built and deployed alongside services in a single workflow, creating a chicken-and-egg problem:

- Gateway builds before services are deployed
- Gateway doesn't have access to newly deployed service URLs
- Gateway federation breaks or points to stale URLs
- Manual intervention required to rebuild gateway after service updates

**Impact**: Broken deployments, manual toil, increased deployment time, unreliable service federation.

---

## Solution Overview

Implement a **two-phase deployment architecture**:

1. **Phase 1: Services Deployment** - Deploy all backend services, extract their Cloud Run URLs, save to Secret Manager
2. **Phase 2: Gateway Deployment** - Fetch service URLs from Secret Manager, build gateway with correct URLs, deploy gateway

This enables:
- ✅ Automatic gateway rebuilds after service updates
- ✅ Zero manual intervention in staging
- ✅ Reliable service URL propagation
- ✅ Clear separation of concerns
- ✅ Rollback capability for gateway independently

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Services Deployment                                │
└─────────────────────────────────────────────────────────────┘
Push to staging
    ↓
Build & Push Services (EXCLUDE gateway)
    ↓
Generate tfvars (services only)
    ↓
Commit tfvars
    ↓
Tofu Apply Services → Deploy to Cloud Run
    ↓
Extract Service URLs from Terraform State
    ↓
Save URLs to Secret Manager (JSON)
    ↓
Trigger: Gateway Rebuild Workflow ✨

┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Gateway Deployment                                 │
└─────────────────────────────────────────────────────────────┘
Gateway Deploy Workflow Triggered
    ↓
Fetch Service URLs from Secret Manager
    ↓
Build Gateway Image (inject URLs as env vars)
    ↓
Push Gateway Image to Artifact Registry
    ↓
Generate tfvars (gateway only)
    ↓
Commit tfvars
    ↓
Tofu Apply Gateway (auto-approve in staging)
    ↓
Verify Gateway Health (/healthcheck + /graphql test)
```

---

## Stories

### ✅ Story 1: Makefile Environment Improvements
**Status**: ✅ Complete
**Priority**: HIGH
**Effort**: 2 hours

**Goal**: Support `make local` and `make staging` with proper Supabase authentication for gateway/web/mobile.

**Tasks**:
- [x] Update `make local` to use local Docker DBs + real Supabase auth
- [x] Update `make staging` to use live DBs + real Supabase auth
- [x] Create/update `.env.local` with Supabase variables
- [x] Update `.env.staging` with Supabase variables
- [x] Test both modes end-to-end

**Acceptance Criteria**:
- ✅ `make local` starts with local DBs + Supabase JWT auth working
- ✅ `make staging` connects to live external services
- ✅ Gateway can authenticate users in both modes
- ✅ Services respond to `/sdl` for schema introspection

---

### 🔄 Story 2: Service Deployment Workflow Updates
**Status**: 🔄 In Progress
**Priority**: CRITICAL
**Effort**: 3 hours

**Goal**: Exclude gateway from service deployment and add service URL extraction.

**Tasks**:
- [ ] Modify `staging-deploy.yml`: Exclude `mesh_gateway` from build matrix
- [ ] Modify `production-deploy.yml`: Same exclusion
- [ ] Update `tofu-apply-staging.yml`: Add job to extract service URLs post-apply
- [ ] Create `scripts/extract-service-urls.sh`: Parse Terraform outputs
- [ ] Create `scripts/save-urls-to-secrets.sh`: Save to GCP Secret Manager
- [ ] Test service deployment without gateway

**Acceptance Criteria**:
- ✅ Service deployment completes without building gateway
- ✅ Terraform apply outputs all service URLs
- ✅ Service URLs saved to Secret Manager with correct structure
- ✅ Gateway deployment workflow triggered after URL save

**Files Modified**:
- `.github/workflows/staging-deploy.yml`
- `.github/workflows/production-deploy.yml`
- `.github/workflows/tofu-apply-staging.yml`
- `.github/workflows/tofu-apply-production.yml`

**Files Created**:
- `scripts/extract-service-urls.sh`
- `scripts/save-urls-to-secrets.sh`

---

### ⏳ Story 3: Gateway Build & Push Workflow
**Status**: ⏳ Not Started
**Priority**: CRITICAL
**Effort**: 2 hours

**Goal**: Create automated gateway build workflow that fetches service URLs and builds gateway image.

**Tasks**:
- [ ] Create `.github/workflows/gateway-deploy.yml`
- [ ] Add job: `fetch-service-urls` (from Secret Manager)
- [ ] Add job: `build-gateway` (with service URLs as build args)
- [ ] Add job: `push-gateway` (to Artifact Registry)
- [ ] Add job: `update-tfvars` (gateway image only)
- [ ] Create `scripts/build-gateway-with-urls.sh`
- [ ] Update `mesh/entrypoint.sh` to support build-time URL injection
- [ ] Test workflow end-to-end

**Acceptance Criteria**:
- ✅ Workflow triggers after service URL save
- ✅ Service URLs fetched from Secret Manager
- ✅ Gateway builds with correct service URLs
- ✅ Gateway image pushed to registry with version tag
- ✅ Gateway tfvars updated and committed

**Files Created**:
- `.github/workflows/gateway-deploy.yml`
- `scripts/build-gateway-with-urls.sh`

**Files Modified**:
- `mesh/entrypoint.sh`

---

### ⏳ Story 4: Gateway Tofu Apply Workflow
**Status**: ⏳ Not Started
**Priority**: CRITICAL
**Effort**: 2 hours

**Goal**: Deploy gateway with auto-approval in staging, manual approval in production.

**Tasks**:
- [ ] Create `.github/workflows/tofu-apply-gateway-staging.yml`
- [ ] Create `.github/workflows/tofu-apply-gateway-production.yml`
- [ ] Configure auto-approval for staging (no manual gate)
- [ ] Keep manual approval gate for production
- [ ] Add gateway health check verification
- [ ] Add GraphQL federation test
- [ ] Test rollback capability

**Acceptance Criteria**:
- ✅ Staging gateway deploys automatically (zero manual steps)
- ✅ Production gateway requires manual approval
- ✅ Health checks pass after deployment
- ✅ Gateway can query all services via federation
- ✅ Can rollback to previous gateway version

**Files Created**:
- `.github/workflows/tofu-apply-gateway-staging.yml`
- `.github/workflows/tofu-apply-gateway-production.yml`

---

### ⏳ Story 5: Generate Tfvars Gateway Mode
**Status**: ⏳ Not Started
**Priority**: HIGH
**Effort**: 1 hour

**Goal**: Support gateway-only mode in tfvars generation script.

**Tasks**:
- [ ] Add `--gateway-only` flag to `scripts/generate-tfvars.sh`
- [ ] Output only gateway-related variables when flag is set
- [ ] Preserve all other variables (project, environment, etc.)
- [ ] Test tfvars generation for gateway-only updates

**Acceptance Criteria**:
- ✅ `generate-tfvars.sh staging v1.0.0 --gateway-only` outputs correct tfvars
- ✅ Gateway tfvars contain only gateway image + metadata
- ✅ No service images included in gateway-only mode

**Files Modified**:
- `scripts/generate-tfvars.sh`

---

## Technical Implementation Details

### Secret Manager Schema

```json
// projects/mindmirror-69/secrets/service-urls-staging/versions/latest
{
  "journal_service_url": "https://journal-service-staging-xxx.run.app",
  "agent_service_url": "https://agent-service-staging-xxx.run.app",
  "habits_service_url": "https://habits-service-staging-xxx.run.app",
  "meals_service_url": "https://meals-service-staging-xxx.run.app",
  "movements_service_url": "https://movements-service-staging-xxx.run.app",
  "practices_service_url": "https://practices-service-staging-xxx.run.app",
  "users_service_url": "https://users-service-staging-xxx.run.app"
}
```

### Gateway Build Process

```bash
#!/bin/bash
# scripts/build-gateway-with-urls.sh

ENVIRONMENT=$1  # staging or production
VERSION_TAG=$2

# 1. Fetch service URLs from Secret Manager
gcloud secrets versions access latest \
  --secret="service-urls-${ENVIRONMENT}" \
  --project="${GCP_PROJECT_ID}" > service-urls.json

# 2. Export as environment variables
export JOURNAL_SERVICE_URL=$(jq -r '.journal_service_url' service-urls.json)
export AGENT_SERVICE_URL=$(jq -r '.agent_service_url' service-urls.json)
export HABITS_SERVICE_URL=$(jq -r '.habits_service_url' service-urls.json)
export MEALS_SERVICE_URL=$(jq -r '.meals_service_url' service-urls.json)
export MOVEMENTS_SERVICE_URL=$(jq -r '.movements_service_url' service-urls.json)
export PRACTICES_SERVICE_URL=$(jq -r '.practices_service_url' service-urls.json)
export USERS_SERVICE_URL=$(jq -r '.users_service_url' service-urls.json)

# 3. Build gateway with URLs
docker build -t gateway:${VERSION_TAG} \
  --build-arg JOURNAL_SERVICE_URL=${JOURNAL_SERVICE_URL} \
  --build-arg AGENT_SERVICE_URL=${AGENT_SERVICE_URL} \
  --build-arg HABITS_SERVICE_URL=${HABITS_SERVICE_URL} \
  --build-arg MEALS_SERVICE_URL=${MEALS_SERVICE_URL} \
  --build-arg MOVEMENTS_SERVICE_URL=${MOVEMENTS_SERVICE_URL} \
  --build-arg PRACTICES_SERVICE_URL=${PRACTICES_SERVICE_URL} \
  --build-arg USERS_SERVICE_URL=${USERS_SERVICE_URL} \
  -f mesh/Dockerfile mesh/

# 4. Push to registry
docker push ${REGISTRY}/mesh:${VERSION_TAG}
```

### Workflow Trigger Chain

```
staging-deploy.yml → build services → push images → update tfvars
    ↓
tofu-apply-staging.yml → deploy services → extract URLs → save to secrets
    ↓ (workflow_run trigger)
gateway-deploy.yml → fetch URLs → build gateway → push image → update tfvars
    ↓ (workflow_run trigger)
tofu-apply-gateway-staging.yml → deploy gateway (auto-approve)
```

---

## Success Metrics

1. **Automation**: Zero manual steps for staging gateway deployment
2. **Speed**: Gateway rebuild completes within 5 minutes of service deployment
3. **Reliability**: 100% success rate for gateway federation after rebuild
4. **Rollback Time**: < 2 minutes to rollback gateway to previous version
5. **Zero Downtime**: Service updates don't impact gateway availability

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gateway build fails to fetch URLs | HIGH | Fallback URLs, alerts, maintain previous version |
| Service URL format changes | MEDIUM | URL validation, schema validation, health checks |
| Workflow trigger chain breaks | MEDIUM | Manual trigger capability, monitoring |
| Secrets access fails | HIGH | Test WIF permissions, fallback to manual deploy |
| Schema composition fails | HIGH | Pre-deployment schema validation, rollback |

---

## Timeline

| Date | Milestone |
|------|-----------|
| 2025-10-29 | Story 1: Makefile updates complete |
| 2025-10-29 EOD | Stories 2-5: Gateway GitOps workflows complete |
| 2025-10-30 AM | Testing and validation on staging |
| 2025-10-30 PM | Production deployment |

---

## Related Documentation

- [CHECKPOINT.md](../CHECKPOINT.md) - Current deployment state
- [CLAUDE.md](../CLAUDE.md) - Project overview and architecture
- [Gateway Rebuild Strategy](./epic-gateway-rebuild-automation.md) - This document
- [GitHub Actions Workflows](../../.github/workflows/) - CI/CD implementation

---

**Last Updated**: 2025-10-29
**Status**: 🔄 In Progress - Story 1 Complete, Starting Story 2
