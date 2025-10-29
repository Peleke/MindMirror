# GitOps Deployment Checkpoint

**Date**: 2025-10-29
**Branch**: `staging`
**Last Commit**: `0c7015f` - "fix(infra): pass environment variable to base module"
**Status**: 🚀 Environment isolation implemented, deployment in progress

---

## Current State

### ✅ Completed Tasks

1. **Fixed Docker Build Issues**
   - `mesh_gateway`: Added `BUILD_CONTEXT="mesh"` for yarn.lock access
   - `journal_service`: Corrected Dockerfile path from `src/journal_service/` to `journal_service/`

2. **Fixed Git Permissions**
   - Added `contents: write` permission to `update-tfvars` job
   - Enabled automated tfvars commits back to repo

3. **Implemented Workflow Chaining**
   - Changed `tofu-apply-staging.yml` from `push` trigger to `workflow_run`
   - Deploy to Staging → automatically triggers → Tofu Apply - Staging
   - Added `workflow_dispatch` for manual triggering

4. **Excluded Deprecated Service**
   - Removed `celery_worker` from build matrix (deprecated, slow builds)

5. **Fixed Critical Infrastructure Bug** 🎯
   - **Problem**: `scripts/generate-tfvars.sh` had incorrect GCP project IDs
   - **Fix**:
     - Staging: `mindmirror-staging` → `mindmirror-69` (project #3858903851)
     - Production: `mindmirror-69` → `mindmirror-prod` (project #435339726777)
   - **Result**: Regenerated `infra/staging.auto.tfvars` with correct configuration

6. **Implemented Environment Isolation** 🎯
   - **Problem**: Resources had no environment suffix → naming conflicts (409 errors)
   - **Fix**:
     - Added `environment` variable to all modules
     - Added `-${var.environment}` suffix to all resources:
       - GCS bucket: `traditions-{project}-{env}`
       - Service accounts: `{service}-{env}`
       - Pub/Sub topics: `{topic}-{env}`
     - Updated data sources to reference new naming
   - **Result**: Staging and production can coexist in same GCP project

7. **Fixed IAM Permissions** 🎯
   - **Problem**: GitHub Actions SA couldn't create service accounts (403 errors)
   - **Fix**:
     - Granted `roles/iam.serviceAccountAdmin` to `github-actions-staging` SA
     - Updated `infra-v2/bootstrap/06-bootstrap-wif.sh` for future deployments
   - **Result**: Terraform can now create service accounts

8. **Improved CI Change Detection**
   - Added comprehensive skip patterns for non-service files
   - Eliminated "Unknown file pattern" warnings for infra/docs/config changes
   - Maintains full branch comparison for safety

### 🔄 In Progress

**Deploy to Staging** (Run #18915265035)
- Status: Building images for changed services
- Commit: `0c7015f`
- Expected: Will auto-trigger Tofu Apply after completion
- All environment isolation fixes are included

### 📦 Latest Build

**Deploy to Staging** (Run #18860100802)
- Status: ✅ Completed successfully
- Commit: `a0133d0`
- Version Tag: `v-a0133d0`
- Duration: ~2 minutes
- Images Built & Pushed:
  - `journal_service`
  - `agent_service`
  - `gateway` (mesh)
  - `habits_service`
  - `meals_service`
  - `users_service`
  - `movements_service`
  - `practices_service`
  - ~~`celery_worker`~~ (excluded)

---

## GCP Project Configuration

### Staging Environment
- **Project ID**: `mindmirror-69`
- **Project Number**: `3858903851`
- **Region**: `us-east4`
- **Artifact Registry**: `us-east4-docker.pkg.dev/mindmirror-69/mindmirror`
- **GCS Bucket**: `traditions-mindmirror-69`
- **Service Account**: `github-actions-staging@mindmirror-69.iam.gserviceaccount.com`

### Production Environment
- **Project ID**: `mindmirror-prod`
- **Project Number**: `435339726777`
- **Region**: `us-east4`
- **Artifact Registry**: `us-east4-docker.pkg.dev/mindmirror-prod/mindmirror`
- **GCS Bucket**: `traditions-mindmirror-prod`
- **Service Account**: `github-actions-production@mindmirror-prod.iam.gserviceaccount.com`

---

## Workflow Architecture

### Current Flow (Staging)

```
┌─────────────────────────┐
│  Push to staging branch │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Deploy to Staging      │
│  ─────────────────────  │
│  1. Detect changes      │
│  2. Build Docker images │
│  3. Push to registry    │
│  4. Generate tfvars     │
│  5. Commit tfvars       │
└───────────┬─────────────┘
            │ workflow_run trigger
            ▼
┌─────────────────────────┐
│  Tofu Apply - Staging   │
│  ─────────────────────  │
│  1. Wait for approval ⏸️│  ← YOU ARE HERE
│  2. Tofu Init           │
│  3. Tofu Plan           │
│  4. Pre-apply checklist │
│  5. Tofu Apply          │
│  6. Verify deployment   │
└─────────────────────────┘
```

### Bootstrap Note

**Known Issue**: `workflow_run` trigger only works for workflows that existed BEFORE the triggering workflow started.

**Current Workaround**: Manual trigger via:
```bash
gh workflow run tofu-apply-staging.yml --ref staging
```

**Future Runs**: Will trigger automatically (workflow file now exists in staging branch)

---

## Next Steps

### Immediate (When You Return)

1. **Approve Staging Deployment**
   - Navigate to: https://github.com/Peleke/MindMirror/actions/runs/18860234790
   - Click "Review deployments"
   - Select "staging" environment
   - Click "Approve and deploy"

2. **Monitor Terraform Plan**
   - Review the plan output in the workflow logs
   - Verify all resources target `mindmirror-69` project
   - Check that image tags use `v-a0133d0`
   - Confirm no unexpected resource changes

3. **Verify Deployment Success**
   - Wait for apply to complete (~5-10 minutes)
   - Check Cloud Run services at: https://console.cloud.google.com/run?project=mindmirror-69
   - Verify all services are running with new image tags

4. **Test Staging Services**
   - Check service health endpoints
   - Verify GraphQL gateway connectivity
   - Test basic functionality

### Short Term

5. **Validate Automatic Workflow Chaining**
   - Make a minor change to staging branch
   - Push and verify `Deploy to Staging` → `Tofu Apply - Staging` triggers automatically
   - If not, manually trigger once more (bootstrap limitation)

6. **Production Deployment Prep**
   - Review production workflow: `.github/workflows/production-deploy.yml`
   - Verify WIF configuration for production
   - Ensure production backend state bucket exists

### Medium Term

7. **Documentation Updates**
   - Update deployment runbooks with new workflow
   - Document manual approval process
   - Add troubleshooting guide for common issues

8. **Infrastructure Improvements**
   - Consider adding smoke tests post-deployment
   - Implement automated rollback on failure
   - Add Slack/Discord notifications for deployments

---

## Key Files Modified

### Primary Changes
- `.github/workflows/staging-deploy.yml` - Fixed build contexts, added celery exclusion
- `.github/workflows/production-deploy.yml` - Same fixes as staging
- `.github/workflows/tofu-apply-staging.yml` - Workflow chaining implementation
- `.github/workflows/tofu-apply-production.yml` - Workflow chaining implementation
- `scripts/generate-tfvars.sh` - **CRITICAL: Fixed project IDs**
- `infra/staging.auto.tfvars` - Regenerated with correct project

### Configuration Files
- `infra/staging.backend.hcl` - Backend state configuration
- `infra/production.backend.hcl` - Backend state configuration

---

## Troubleshooting Reference

### Issue: Tofu Apply Not Triggering

**Symptoms**: Deploy to Staging succeeds but Tofu Apply - Staging doesn't run

**Causes**:
1. Bootstrap limitation (workflow_run requires pre-existing workflow)
2. Workflow file was added in same push

**Solution**: Manually trigger once with:
```bash
gh workflow run tofu-apply-staging.yml --ref staging
```

### Issue: Secret Manager Permission Denied

**Symptoms**: `Error 403: Permission denied on resource project mindmirror-staging`

**Cause**: Incorrect project ID in tfvars

**Solution**: Already fixed! `generate-tfvars.sh` now uses correct project IDs

### Issue: Build Failures for mesh_gateway

**Symptoms**: `yarn.lock: not found`

**Cause**: Build context was repo root, but yarn.lock is in `mesh/`

**Solution**: Already fixed! Added `BUILD_CONTEXT="mesh"` to workflow

---

## Environment Variables (Reference)

### GitHub Secrets (Repository Level)
- `GCP_STAGING_PROJECT_NUM`: `3858903851`
- `GCP_PRODUCTION_PROJECT_NUM`: `435339726777`

### Workflow Environment Variables

**Staging**:
```yaml
GCP_PROJECT_ID: mindmirror-69
GCP_REGION: us-east4
ENVIRONMENT: staging
TOFU_VERSION: 1.6.0
```

**Production**:
```yaml
GCP_PROJECT_ID: mindmirror-prod
GCP_REGION: us-east4
ENVIRONMENT: production
TOFU_VERSION: 1.6.0
```

---

## Success Criteria

### ✅ Deployment Considered Successful When:

1. **Build Phase**
   - All Docker images build without errors
   - Images pushed to Artifact Registry with correct tags
   - Tfvars file generated and committed

2. **Plan Phase**
   - Tofu plan completes without errors
   - Plan targets correct GCP project (`mindmirror-69` for staging)
   - Resource changes are expected and intentional

3. **Apply Phase**
   - Tofu apply completes successfully
   - All Cloud Run services show "Ready" status
   - Health check endpoints return 200 OK

4. **Verification Phase**
   - Services accessible via public URLs
   - GraphQL gateway responds to queries
   - No errors in Cloud Run logs

---

## Quick Commands

```bash
# Check current workflow status
gh run list --branch staging --limit 5

# View specific run details
gh run view 18860234790

# Manually trigger tofu-apply
gh workflow run tofu-apply-staging.yml --ref staging

# Check Cloud Run services
gcloud run services list --project=mindmirror-69 --region=us-east4

# View workflow logs
gh run view 18860234790 --log

# Check git status
git status && git branch
```

---

## Notes for Next Session

- The project ID fix was the critical blocker - Secret Manager errors should be resolved
- Workflow chaining is implemented but needs one more successful run to fully bootstrap
- Consider adding pre-commit hooks to validate tfvars project IDs
- May want to add integration tests that run post-deployment
- Keep an eye on build times - removed celery_worker but builds still take ~2 minutes

---

**Last Updated**: 2025-10-28 00:35 UTC
**Next Action**: Approve deployment at https://github.com/Peleke/MindMirror/actions/runs/18860234790
