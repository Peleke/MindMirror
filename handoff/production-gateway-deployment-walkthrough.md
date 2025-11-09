# Production Gateway Deployment - Full Pipeline Walkthrough

**Date:** 2025-10-31
**Status:** Ready to execute
**Created Files:**
- ✅ `.github/workflows/gateway-deploy-production.yml`
- ✅ `.github/workflows/tofu-apply-gateway-production.yml`

---

## ✅ Script Verification Complete

**Script:** `scripts/build-gateway-with-urls.sh`

✅ Supports both environments:
- `staging` → Project: `mindmirror-69`, Secret: `service-urls-staging`
- `production` → Project: `mindmirror-prod`, Secret: `service-urls-production`

✅ No changes needed to scripts!

---

## 📋 Pre-Flight Requirements

### 1. GitHub Environment Setup (REQUIRED)

Before running production workflows, configure GitHub Environment:

```
1. Go to: https://github.com/{your-org}/MindMirror/settings/environments
2. Click "New environment"
3. Name: "production"
4. Configure:
   ✅ Required reviewers: Add yourself and/or team members
   ✅ Deployment branches: Select "Selected branches" → Add "main"
5. Save
```

**Why:** Without this, the approval gate won't work and deployments will fail.

### 2. GCP Resource Validation (RECOMMENDED)

Verify production GCP resources exist:

```bash
# Set project
gcloud config set project mindmirror-prod

# Verify project exists
gcloud projects describe mindmirror-prod

# Verify Workload Identity Pool
gcloud iam workload-identity-pools list \
  --location=global \
  --project=mindmirror-prod

# Verify service account
gcloud iam service-accounts list \
  --project=mindmirror-prod \
  --filter="email:github-actions-production@"

# Verify Artifact Registry
gcloud artifacts repositories describe mindmirror \
  --location=us-east4 \
  --project=mindmirror-prod

# Verify Secret Manager secrets exist
gcloud secrets list \
  --project=mindmirror-prod \
  --filter="name:service-urls"

# Expected: service-urls-production (created by service deployment)
```

### 3. Verify GitHub Secrets

Required secrets in repo settings:
- ✅ `GCP_STAGING_PROJECT_NUM` (already exists)
- ✅ `GCP_PRODUCTION_PROJECT_NUM` (verify exists)

---

## 🚀 Full Pipeline Execution Plan

### Phase 1: Test Staging Pipeline (Feature Branch → Staging)

**Goal:** Verify staging workflows still work with new production files present

#### Step 1.1: Create Feature Branch

```bash
# Currently on staging branch
git checkout -b feature/add-production-gateway-workflows

# Add new workflow files
git add .github/workflows/gateway-deploy-production.yml
git add .github/workflows/tofu-apply-gateway-production.yml
git add handoff/

# Commit
git commit -m "feat(workflows): add production gateway deployment workflows

- Add gateway-deploy-production.yml (phase 3)
- Add tofu-apply-gateway-production.yml (phase 4)
- Add approval gates for production deployments
- Add comprehensive issue tracking on success/failure
"

# Push feature branch
git push origin feature/add-production-gateway-workflows
```

#### Step 1.2: Create PR to Staging

```bash
# Create PR via GitHub CLI
gh pr create \
  --base staging \
  --head feature/add-production-gateway-workflows \
  --title "feat: Add production gateway deployment workflows" \
  --body "## Summary
Adds production gateway deployment workflows (phases 3-4) with approval gates.

## Changes
- ✅ \`.github/workflows/gateway-deploy-production.yml\`
- ✅ \`.github/workflows/tofu-apply-gateway-production.yml\`
- ✅ Approval gates via GitHub Environment
- ✅ Comprehensive issue tracking

## Testing
- [ ] Review workflow files
- [ ] Verify no impact on staging workflows
- [ ] Confirm approval gate configuration

## Verification
Script validation:
- ✅ \`scripts/build-gateway-with-urls.sh\` supports both environments
- ✅ No script changes required

## Next Steps After Merge
1. Configure GitHub Environment 'production'
2. Validate GCP production resources
3. Merge staging → main to test production workflows
"
```

#### Step 1.3: Merge PR and Watch Staging Workflows

```bash
# After PR approval, merge via GitHub UI or:
gh pr merge --squash --delete-branch

# OR manually:
git checkout staging
git merge feature/add-production-gateway-workflows
git push origin staging
```

**What to Watch:**

Navigate to: `https://github.com/{your-org}/MindMirror/actions`

**Expected Workflow Cascade (Staging):**

1. **Deploy to Staging** (triggered by push to staging)
   - Builds service images
   - Updates `staging.auto.tfvars`
   - Creates PR or commits directly

2. **Tofu Apply - Staging** (triggered by "Deploy to Staging" completion)
   - Plans infrastructure changes
   - Auto-applies (no approval needed)
   - Saves service URLs to Secret Manager

3. **Deploy Gateway to Staging** (triggered by "Tofu Apply - Staging" completion)
   - Builds gateway with service URLs
   - Updates `staging.auto.tfvars` (gateway image)
   - Commits changes

4. **Tofu Apply - Gateway (Staging)** (triggered by "Deploy Gateway to Staging")
   - Plans gateway deployment
   - Auto-applies (no approval needed)
   - Health checks gateway

**Verification Points:**
- ✅ All 4 workflows complete successfully
- ✅ No errors in workflow logs
- ✅ Gateway health check passes
- ✅ New production workflows NOT triggered (staging branch only)

---

### Phase 2: Deploy to Production (Staging → Main)

**Goal:** Trigger production deployment with approval gates

#### Step 2.1: Ensure GitHub Environment is Configured

**CRITICAL:** Before proceeding, verify:
```bash
# Check if production environment exists (via GitHub CLI)
gh api repos/{owner}/{repo}/environments | jq '.environments[] | select(.name=="production")'
```

If empty, **STOP** and configure GitHub Environment (see Pre-Flight Requirements #1).

#### Step 2.2: Create PR from Staging to Main

```bash
# Switch to staging
git checkout staging
git pull origin staging

# Create PR to main
gh pr create \
  --base main \
  --head staging \
  --title "feat: Production gateway deployment workflows" \
  --body "## Summary
Adds production gateway deployment workflows with approval gates.

## Workflows Added
- ✅ \`gateway-deploy-production.yml\` - Phase 3: Build gateway for production
- ✅ \`tofu-apply-gateway-production.yml\` - Phase 4: Deploy gateway with approval

## Approval Gates
- 🛡️ Production environment configured in GitHub
- 🛡️ Manual approval required before deployment
- 🛡️ Issue tracking on success/failure

## Pre-Merge Checklist
- [ ] GitHub Environment 'production' configured with reviewers
- [ ] GCP production resources validated
- [ ] \`GCP_PRODUCTION_PROJECT_NUM\` secret exists
- [ ] Ready to deploy to production

## Deployment Flow After Merge
1. Services deploy to production (requires approval)
2. Service URLs saved to Secret Manager
3. Gateway builds with production URLs
4. Gateway deployment (requires SECOND approval)
5. Health checks verify gateway

## Rollback Plan
- Revert \`production.auto.tfvars\` to previous version
- Manually trigger gateway workflow with old image
- Or use \`gcloud run deploy\` with known-good image
"
```

#### Step 2.3: Merge and Watch Production Workflows

```bash
# After PR review and approval, merge
gh pr merge --squash

# OR via UI, then pull locally:
git checkout main
git pull origin main
```

**What to Watch:**

Navigate to: `https://github.com/{your-org}/MindMirror/actions`

**Expected Workflow Cascade (Production):**

1. **Deploy to Production** (triggered by push to main)
   - Builds service images for production
   - Updates `production.auto.tfvars`
   - Creates PR to main

2. **Wait for PR Review + Merge** (manual step)
   - Review tfvars changes
   - Merge PR

3. **Tofu Apply - Production** (triggered by merge)
   - **⏸️ PAUSES for manual approval** (GitHub Environment gate)
   - Navigate to Actions tab → Click "Review deployments" button
   - Approve deployment
   - Plans infrastructure changes
   - Applies to production
   - Saves service URLs to `service-urls-production` secret
   - Creates GitHub issue with deployment summary

4. **Deploy Gateway to Production** (triggered by "Tofu Apply - Production" completion)
   - Builds gateway with production service URLs
   - Updates `production.auto.tfvars` (gateway image)
   - Commits changes to main

5. **Wait for Gateway PR Review + Merge** (manual step)
   - Review gateway tfvars changes
   - Merge PR

6. **Tofu Apply - Gateway (Production)** (triggered by merge)
   - **⏸️ PAUSES for SECOND manual approval** (GitHub Environment gate)
   - Navigate to Actions tab → Click "Review deployments" button
   - Approve gateway deployment
   - Plans gateway deployment
   - Applies to production
   - Health checks gateway
   - Creates GitHub issue with gateway deployment summary

---

## 🎯 Success Criteria

### Staging Pipeline Success
- [ ] All 4 staging workflows complete (green checkmarks)
- [ ] No workflow failures or errors
- [ ] Gateway health endpoint returns 200 OK
- [ ] GraphQL schema accessible at gateway URL

### Production Pipeline Success
- [ ] Services deploy after first approval
- [ ] Service URLs saved to Secret Manager
- [ ] Gateway builds with production URLs
- [ ] Gateway deploys after second approval
- [ ] Gateway health endpoint returns 200 OK
- [ ] Two success issues created (services + gateway)
- [ ] No failure issues created

---

## 🚨 Troubleshooting

### "Environment 'production' not found"

**Problem:** GitHub Environment not configured

**Solution:**
1. Go to repo Settings → Environments
2. Create "production" environment
3. Add required reviewers
4. Re-run failed workflow manually

### "Secret not found: GCP_PRODUCTION_PROJECT_NUM"

**Problem:** GitHub secret missing

**Solution:**
1. Go to repo Settings → Secrets and variables → Actions
2. Add `GCP_PRODUCTION_PROJECT_NUM` secret
3. Get value from GCP Console (project number, not ID)

### "Failed to fetch service URLs from Secret Manager"

**Problem:** `service-urls-production` secret doesn't exist yet

**Solution:**
- This is expected on FIRST production deployment
- Secret is created by `tofu-apply-production.yml` workflow
- If services deployed successfully, secret should exist
- Verify: `gcloud secrets list --project=mindmirror-prod`

### Gateway health check fails

**Problem:** Gateway not ready yet (cold start)

**Solution:**
- Wait 30-60 seconds and check manually:
  ```bash
  GATEWAY_URL=$(gcloud run services describe gateway \
    --project=mindmirror-prod \
    --region=us-east4 \
    --format="value(status.url)")

  curl -s "${GATEWAY_URL}/healthcheck" | jq '.'
  ```
- If still failing, check Cloud Run logs in GCP Console

### Workflow stuck on "Waiting for approval"

**Problem:** Approval not granted in GitHub UI

**Solution:**
1. Go to Actions tab in GitHub
2. Click on the running workflow
3. Look for "Review deployments" button (usually bright green/orange)
4. Click button, select "production" environment, approve

---

## 📊 Monitoring During Deployment

### GitHub Actions
- Watch: `https://github.com/{your-org}/MindMirror/actions`
- Real-time logs for each workflow step
- Approval buttons appear in UI when needed

### GCP Console
- Cloud Run: `https://console.cloud.google.com/run?project=mindmirror-prod`
- Watch service revisions being deployed
- Check traffic routing (should be 100% to new revision)

### Secret Manager
- Secrets: `https://console.cloud.google.com/security/secret-manager?project=mindmirror-prod`
- Verify `service-urls-production` contains all 7 service URLs

### Gateway Health
```bash
# After gateway deploys
GATEWAY_URL=$(gcloud run services describe gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="value(status.url)")

# Health check
curl -s "${GATEWAY_URL}/healthcheck" | jq '.'

# GraphQL introspection
curl -s "${GATEWAY_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{__schema{types{name}}}"}' | jq '.'
```

---

## 🎉 Post-Deployment Verification

After successful production deployment:

1. **Verify all services are running:**
   ```bash
   gcloud run services list \
     --project=mindmirror-prod \
     --region=us-east4 \
     --format="table(SERVICE,URL,LAST_DEPLOYED)"
   ```

2. **Test gateway federation:**
   ```bash
   # Get gateway URL
   GATEWAY_URL=$(gcloud run services describe gateway \
     --project=mindmirror-prod \
     --region=us-east4 \
     --format="value(status.url)")

   # Test health
   curl "${GATEWAY_URL}/healthcheck"

   # Test GraphQL
   curl "${GATEWAY_URL}/graphql" -H "Content-Type: application/json" \
     -d '{"query": "{__typename}"}'
   ```

3. **Check GitHub issues created:**
   - Should see 2 success issues (services + gateway)
   - Tagged with `production`, `deployment`, `success`

4. **Verify tfvars updated:**
   ```bash
   # Check production.auto.tfvars contains gateway image
   grep "gateway_container_image" infra/production.auto.tfvars
   ```

---

## 🔄 Rollback Procedure

If deployment fails or issues arise:

### Rollback Services
```bash
cd infra
git checkout HEAD~1 -- production.auto.tfvars
git commit -m "rollback: revert production deployment"
git push origin main
# Approve rollback in GitHub Actions
```

### Rollback Gateway Only
```bash
cd infra
# Edit production.auto.tfvars and change gateway_container_image to previous version
git add production.auto.tfvars
git commit -m "rollback: revert gateway to previous version"
git push origin main
# Approve rollback in GitHub Actions
```

### Emergency Manual Rollback
```bash
# Deploy previous known-good gateway image
gcloud run deploy gateway \
  --image=us-east4-docker.pkg.dev/mindmirror-prod/mindmirror/mesh:v1.0.0-PREVIOUS_SHA \
  --region=us-east4 \
  --project=mindmirror-prod
```

---

## 📝 Summary of Files Created

```
.github/workflows/
├── gateway-deploy-production.yml         # NEW: Phase 3 - Build production gateway
└── tofu-apply-gateway-production.yml     # NEW: Phase 4 - Deploy production gateway

handoff/
├── production-deployment-readiness-epic.md
└── production-gateway-deployment-walkthrough.md  # This file
```

**Existing files (no changes):**
- ✅ `scripts/build-gateway-with-urls.sh` - Already supports production
- ✅ `.github/workflows/tofu-apply-production.yml` - Already has approval gates
- ✅ `infra/production.backend.hcl` - Backend config exists
- ✅ `infra/defaults.tfvars` - Service naming correct (no suffix)

---

## 🎯 Ready to Execute

Everything is ready! Follow Phase 1 (staging test) then Phase 2 (production deployment).

**Estimated Time:**
- Phase 1 (Staging): ~15-20 minutes (4 workflow cascade)
- Phase 2 (Production): ~25-30 minutes (6 steps with 2 approvals)

**Total:** ~45-50 minutes for full pipeline test
