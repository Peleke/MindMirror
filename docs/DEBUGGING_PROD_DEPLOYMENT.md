# Production Deployment Debugging Plan

**Date**: 2025-10-31
**Status**: CRITICAL - Production deployment completely broken
**Priority**: P0 - Fix tomorrow before any other work

---

## Executive Summary

Production deployment has **THREE CRITICAL FAILURES** preventing any infrastructure deployment:

1. **INFRASTRUCTURE MISSING**: Artifact Registry repository doesn't exist in production project
2. **INFRASTRUCTURE MISSING**: GCS bucket for Terraform state doesn't exist
3. **WORKFLOW CHAIN BROKEN**: Workflows skip or fail due to trigger conditions not being met

These are **infrastructure prerequisites** that must exist before any workflow can succeed.

---

## Critical Issues Identified

### Issue 1: Missing Artifact Registry Repository

**Symptom**:
```
name unknown: Repository "mindmirror" not found
```

**Evidence**:
- Run 18987975291 (production-deploy.yml) failed when pushing Docker images
- `gcloud artifacts repositories list --project=mindmirror-prod --location=us-east4` returns 0 items
- Workflow expects: `us-east4-docker.pkg.dev/mindmirror-prod/mindmirror`

**Root Cause**:
Artifact Registry repository `mindmirror` does not exist in production project.

**Impact**:
- **Phase 1 (Build)**: Cannot push service images → workflow fails
- **Phase 2 (Tofu Apply)**: Skips because Phase 1 failed
- **Phase 3 (Gateway Build)**: Succeeds but gateway image has nowhere to go
- **Phase 4 (Gateway Deploy)**: Fails because no valid image exists

**Fix Required**:
```bash
gcloud artifacts repositories create mindmirror \
  --repository-format=docker \
  --location=us-east4 \
  --project=mindmirror-prod \
  --description="Production Docker images for MindMirror services"
```

**Verification**:
```bash
gcloud artifacts repositories describe mindmirror \
  --location=us-east4 \
  --project=mindmirror-prod
```

---

### Issue 2: Missing GCS Bucket for Terraform State

**Symptom**:
```
Error: Failed to get existing workspaces: querying Cloud Storage failed:
googleapi: Error 403: github-actions-production@mindmirror-prod.iam.gserviceaccount.com
does not have storage.objects.list access to the Google Cloud Storage bucket.
Permission 'storage.objects.list' denied on resource (or it may not exist)., forbidden
```

**Evidence**:
- Run 18987992142 (tofu-apply-gateway-production.yml) failed during `tofu init`
- Backend config expects: `bucket = "mindmirror-tofu-state"` (infra/production.backend.hcl:4)
- `gcloud storage buckets list --project=mindmirror-prod` returns nothing
- Service account HAS `roles/storage.admin` on PROJECT level

**Root Cause**:
GCS bucket `mindmirror-tofu-state` does not exist in production project. The permission error is misleading - the bucket literally doesn't exist.

**Impact**:
- **Phase 4 (Gateway Deploy - Tofu Init)**: Cannot initialize Terraform state → fails immediately
- All Terraform operations blocked until bucket exists

**Fix Required**:
```bash
# Create the state bucket
gcloud storage buckets create gs://mindmirror-tofu-state \
  --project=mindmirror-prod \
  --location=us-east4 \
  --uniform-bucket-level-access

# Enable versioning for state file safety
gcloud storage buckets update gs://mindmirror-tofu-state \
  --versioning

# Grant service account access (should inherit from roles/storage.admin but belt-and-suspenders)
gcloud storage buckets add-iam-policy-binding gs://mindmirror-tofu-state \
  --member="serviceAccount:github-actions-production@mindmirror-prod.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin" \
  --project=mindmirror-prod
```

**Verification**:
```bash
# Verify bucket exists
gcloud storage buckets describe gs://mindmirror-tofu-state

# Test Terraform can access it
cd infra
tofu init -backend-config=production.backend.hcl
```

---

### Issue 3: Workflow Trigger Chain Broken

**Symptom**:
- Production-deploy.yml FAILS (missing registry)
- Tofu-apply-production.yml SKIPS
- Gateway-deploy-production.yml SUCCEEDS (but builds nowhere)
- Tofu-apply-gateway-production.yml FAILS (missing state bucket)

**Evidence**:
```
Run 18987975291 (production-deploy.yml): FAILURE (missing artifact registry)
Run 18987990697 (tofu-apply-production.yml): SKIPPED
Run 18987991093 (gateway-deploy-production.yml): SUCCESS
Run 18987992142 (tofu-apply-gateway-production.yml): FAILURE (missing state bucket)
```

**Analysis of Workflow Chain**:

```yaml
# tofu-apply-production.yml (line 19)
if: ${{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}
```

**Why it skips**:
- Triggered by `workflow_run` from "Deploy to Production" (production-deploy.yml)
- production-deploy.yml conclusion == 'failure' (missing artifact registry)
- `github.event.workflow_run.conclusion == 'success'` evaluates to FALSE
- `github.event_name == 'workflow_dispatch'` evaluates to FALSE (triggered, not dispatched)
- Entire `if` condition is FALSE → workflow skips

**Why gateway-deploy-production.yml succeeds**:
- It's triggered from the WRONG workflow:
  ```yaml
  # gateway-deploy-production.yml (line 5)
  workflows: ["Tofu Apply - Production"]
  ```
- But tofu-apply-production.yml is SKIPPING, not running with conclusion
- Gateway workflow sees no workflow_run event, so it's likely also skipping OR running independently

**Root Cause**:
The 4-phase workflow chain depends on each phase succeeding, but Phase 1 fails immediately due to missing infrastructure.

**Fix Required**:
Fix Issues 1 and 2 first (create registry and bucket), then the workflow chain will complete naturally.

---

## Complete Dependency Chain

```
┌─────────────────────────────────────────────────────────────┐
│ PREREQUISITES (MUST EXIST BEFORE ANY WORKFLOW RUNS)         │
├─────────────────────────────────────────────────────────────┤
│ 1. Artifact Registry: mindmirror                            │
│    - Location: us-east4                                     │
│    - Format: docker                                         │
│ 2. GCS Bucket: mindmirror-tofu-state                        │
│    - Location: us-east4                                     │
│    - Versioning: enabled                                    │
│ 3. Service Account: github-actions-production               │
│    - Created ✅ (via bootstrap script)                      │
│    - Roles ✅ (storage.admin, artifactregistry.admin, etc.) │
│ 4. WIF Pool/Provider: github-pool/github-oidc               │
│    - Created ✅ (via bootstrap script)                      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Build Service Images (production-deploy.yml)      │
├─────────────────────────────────────────────────────────────┤
│ Trigger: Push to main (excluding tfvars)                   │
│ Job: build-and-push (matrix, excludes mesh_gateway)        │
│ Outputs: Service images in Artifact Registry               │
│ Status: ❌ FAILS - Repository "mindmirror" not found       │
└─────────────────────────────────────────────────────────────┘
         │ success
         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Deploy Services (tofu-apply-production.yml)       │
├─────────────────────────────────────────────────────────────┤
│ Trigger: workflow_run (Deploy to Production succeeded)     │
│ Condition: github.event.workflow_run.conclusion == success │
│ Environment: production (requires approval)                │
│ Jobs:                                                       │
│   - apply: Deploy services via Terraform                   │
│   - extract-service-urls: Save URLs to Secret Manager      │
│ Status: ⏭️ SKIPPED - Phase 1 failed                        │
└─────────────────────────────────────────────────────────────┘
         │ extract-service-urls triggers
         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: Build Gateway (gateway-deploy-production.yml)     │
├─────────────────────────────────────────────────────────────┤
│ Trigger: workflow_run (Tofu Apply - Production completed)  │
│ Trigger (WRONG): workflow_run (Deploy to Production)       │
│ Jobs:                                                       │
│   - build-gateway: Build with service URLs                 │
│   - update-gateway-tfvars: Commit tfvars                   │
│   - trigger-gateway-apply: Trigger Phase 4                 │
│ Status: ✅ SUCCESS (but wrong trigger, image nowhere)      │
└─────────────────────────────────────────────────────────────┘
         │ triggers
         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: Deploy Gateway (tofu-apply-gateway-prod.yml)      │
├─────────────────────────────────────────────────────────────┤
│ Trigger: workflow_run (Deploy Gateway succeeded)           │
│ Environment: production (requires approval)                │
│ Job: apply-gateway (tofu init → plan → apply)              │
│ Status: ❌ FAILS - State bucket doesn't exist              │
└─────────────────────────────────────────────────────────────┘
```

---

## Additional Issues Found

### Gateway Workflow Wrong Trigger
**File**: `.github/workflows/gateway-deploy-production.yml:5`
**Current**:
```yaml
workflows: ["Tofu Apply - Production"]
```

**Problem**: Gateway build should trigger from tofu-apply-production's `extract-service-urls` job completion, but workflow_run only triggers on workflow completion, not job completion.

**Why This Happens**:
The `extract-service-urls` job in tofu-apply-production.yml manually triggers gateway-deploy via `gh workflow run`. The workflow_run trigger in gateway-deploy is likely vestigial from an earlier design.

**Action**: Verify the manual trigger is working correctly. The workflow_run trigger might be redundant.

---

## Action Plan (Execute Tomorrow in Order)

### Step 1: Create Artifact Registry Repository
```bash
# Create registry
gcloud artifacts repositories create mindmirror \
  --repository-format=docker \
  --location=us-east4 \
  --project=mindmirror-prod \
  --description="Production Docker images for MindMirror services"

# Verify
gcloud artifacts repositories describe mindmirror \
  --location=us-east4 \
  --project=mindmirror-prod

# Expected: Repository details showing FORMAT=DOCKER, LOCATION=us-east4
```

### Step 2: Create GCS State Bucket
```bash
# Create bucket
gcloud storage buckets create gs://mindmirror-tofu-state \
  --project=mindmirror-prod \
  --location=us-east4 \
  --uniform-bucket-level-access

# Enable versioning
gcloud storage buckets update gs://mindmirror-tofu-state \
  --versioning

# Verify
gcloud storage buckets describe gs://mindmirror-tofu-state

# Test Terraform access
cd infra
tofu init -backend-config=production.backend.hcl

# Expected: "Terraform has been successfully initialized!"
```

### Step 3: Verify Service Account Permissions
```bash
# Already verified - service account has all required roles:
# - roles/storage.admin ✅
# - roles/artifactregistry.admin ✅
# - roles/run.admin ✅
# - roles/secretmanager.admin ✅
# - roles/iam.serviceAccountUser ✅
# - etc.

# No action required for service account
```

### Step 4: Test Workflow Chain End-to-End
```bash
# Make a trivial change to trigger workflow
echo "# Test deployment" >> README.md
git checkout -b test-prod-deployment
git add README.md
git commit -m "test: trigger production deployment workflow"
git push origin test-prod-deployment

# Merge to main (will trigger production-deploy.yml)
gh pr create --title "Test: Production Deployment" --body "Testing fixed infrastructure"
gh pr merge --auto --squash

# Monitor workflow execution
gh run list --workflow production-deploy.yml --limit 1
gh run watch  # watch latest run

# Expected flow:
# 1. production-deploy.yml: SUCCESS (images push to registry)
# 2. tofu-apply-production.yml: WAITS for approval → approve → SUCCESS
# 3. gateway-deploy-production.yml: SUCCESS (gateway image builds)
# 4. tofu-apply-gateway-production.yml: WAITS for approval → approve → SUCCESS
```

### Step 5: Verify Production Services
```bash
# After all workflows complete, check deployed services
gcloud run services list \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="table(SERVICE,REGION,URL,LAST_DEPLOYED)"

# Expected: All services deployed with recent timestamps

# Test gateway health
GATEWAY_URL=$(gcloud run services describe gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="value(status.url)")

curl -f "$GATEWAY_URL/healthcheck"
# Expected: {"status":"healthy"} or similar
```

---

## Success Criteria

- [ ] Artifact Registry `mindmirror` exists in us-east4
- [ ] GCS bucket `mindmirror-tofu-state` exists with versioning enabled
- [ ] Terraform init succeeds locally with production backend
- [ ] production-deploy.yml completes successfully (images pushed)
- [ ] tofu-apply-production.yml completes after approval (services deployed)
- [ ] gateway-deploy-production.yml completes successfully (gateway image built)
- [ ] tofu-apply-gateway-production.yml completes after approval (gateway deployed)
- [ ] All production services healthy and accessible

---

## Lessons Learned / Prevention

### Why This Happened
1. **Bootstrap Gap**: Bootstrap scripts create service accounts and WIF but don't create GCS buckets or Artifact Registry
2. **Staging Parity**: Staging has these resources (created manually or via earlier setup), production doesn't
3. **Workflow Assumption**: Workflows assume infrastructure exists, don't validate prerequisites

### How to Prevent
1. **Complete Bootstrap Script**: Add GCS bucket and Artifact Registry creation to bootstrap process
2. **Validation Step**: Add workflow step that validates prerequisites exist before attempting operations
3. **Documentation**: Document all infrastructure prerequisites in infra/README.md
4. **IaC Everything**: Create Terraform module for "bootstrap resources" (state bucket, artifact registry, etc.)

### Future Improvements
```bash
# Add to bootstrap script (infra-v2/bootstrap/07-bootstrap-resources.sh):
#!/bin/bash
# Creates foundational resources needed for CI/CD

# 1. Create Artifact Registry
gcloud artifacts repositories create mindmirror \
  --repository-format=docker \
  --location=us-east4 \
  --project=$PROJECT_ID

# 2. Create Terraform state bucket
gcloud storage buckets create gs://${PROJECT_ID}-tofu-state \
  --project=$PROJECT_ID \
  --location=us-east4 \
  --uniform-bucket-level-access

gcloud storage buckets update gs://${PROJECT_ID}-tofu-state \
  --versioning

# 3. Create Secret Manager secrets for service URLs
# etc.
```

---

## Confidence Assessment

**Fix Certainty**: 🟢 **100% - Root causes identified**

**Evidence**:
1. Artifact Registry missing: Verified via `gcloud artifacts repositories list` → 0 results
2. GCS bucket missing: Error message + implicit verification (list returns nothing)
3. Workflow skipping: Explicit `if` condition in tofu-apply-production.yml line 19

**What Could Still Go Wrong**:
- Other missing resources we haven't discovered yet
- Terraform configuration issues once state bucket exists
- Secret Manager secrets might not exist for service URLs
- Network/VPC configuration might be incomplete

**Mitigation**:
Execute steps incrementally, verify each step before proceeding to next.

---

## Related Files

- `.github/workflows/production-deploy.yml` - Phase 1 (builds)
- `.github/workflows/tofu-apply-production.yml` - Phase 2 (service deployment)
- `.github/workflows/gateway-deploy-production.yml` - Phase 3 (gateway build)
- `.github/workflows/tofu-apply-gateway-production.yml` - Phase 4 (gateway deployment)
- `infra/production.backend.hcl` - Terraform state backend config
- `infra/production.auto.tfvars` - Terraform production variables
- `infra-v2/bootstrap/06-bootstrap-wif.sh` - Service account + WIF setup

---

**END OF DEBUGGING PLAN**
