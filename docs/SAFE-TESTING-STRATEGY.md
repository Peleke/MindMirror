# Safe Testing Strategy - GitHub Actions Deployment

**Problem**: Staging environment is LIVE. Need to test automation without breaking it.

**Solution**: Multi-phase rollout with safety gates at each step.

---

## Phase 0: Pre-Flight Checklist (Before ANY automation)

### Backup Current State

```bash
# 1. Export current Tofu state
cd infra
tofu init  # Use current backend config
tofu show > /tmp/staging-state-backup-$(date +%Y%m%d).txt

# 2. Document current Cloud Run services
gcloud run services list \
  --project=mindmirror-staging \
  --region=us-east4 \
  --format=json > /tmp/staging-services-backup-$(date +%Y%m%d).json

# 3. Save current image tags
gcloud run services list \
  --project=mindmirror-staging \
  --region=us-east4 \
  --format="table(SERVICE,IMAGE)" > /tmp/staging-images-backup-$(date +%Y%m%d).txt

# 4. Commit current tfvars as baseline
cp infra/staging.auto.tfvars /tmp/staging-tfvars-baseline-$(date +%Y%m%d).tfvars
```

**Store these backups safely** - they're your rollback point.

---

## Phase 1: Validate WIF Setup (No Tofu Operations)

**Goal**: Prove WIF authentication works without touching infrastructure.

### Step 1.1: Setup WIF for Staging

```bash
export STAGING_PROJECT="mindmirror-staging"
export STAGING_PROJECT_NUM=$(gcloud projects describe $STAGING_PROJECT --format='value(projectNumber)')
export GITHUB_REPO="pelekeyes/MindMirror"  # ← Update with your org/repo

# Create WIF pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create OIDC provider
gcloud iam workload-identity-pools providers create-oidc "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository_owner == '$(echo $GITHUB_REPO | cut -d'/' -f1)'"

# Create service account (if doesn't exist)
gcloud iam service-accounts create github-actions-staging \
  --project=$STAGING_PROJECT \
  --display-name="GitHub Actions - Staging" || echo "Service account already exists"

# Grant minimal permissions for testing (read-only first!)
gcloud projects add-iam-policy-binding $STAGING_PROJECT \
  --member="serviceAccount:github-actions-staging@${STAGING_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/viewer"  # READ-ONLY for testing

# Bind service account to WIF pool (staging branch only)
gcloud iam service-accounts add-iam-policy-binding \
  "github-actions-staging@${STAGING_PROJECT}.iam.gserviceaccount.com" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GITHUB_REPO}" \
  --condition='expression=assertion.ref == "refs/heads/staging",title=staging-branch-only'

# Get WIF provider resource name
gcloud iam workload-identity-pools providers describe "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"
# → Save this for GitHub secrets
```

### Step 1.2: Test WIF Authentication (No Infrastructure Changes)

Create a simple test workflow:

```yaml
# .github/workflows/test-wif-auth.yml
name: Test WIF Authentication

on:
  workflow_dispatch:  # Manual trigger only

jobs:
  test-auth:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/${{ secrets.GCP_STAGING_PROJECT_NUM }}/locations/global/workloadIdentityPools/github-pool/providers/github-oidc'
          service_account: 'github-actions-staging@mindmirror-staging.iam.gserviceaccount.com'

      - name: Test GCP Access
        run: |
          gcloud projects describe mindmirror-staging
          echo "✅ WIF authentication successful!"

      - name: List Cloud Run Services (read-only)
        run: |
          gcloud run services list --project=mindmirror-staging --region=us-east4
          echo "✅ Can read Cloud Run services"
```

**Test**:
```bash
# Add GitHub secrets first:
# - GCP_STAGING_PROJECT_NUM: <your staging project number>

# Trigger workflow manually
gh workflow run test-wif-auth.yml

# Check results
gh run list --workflow=test-wif-auth.yml
```

**Success criteria**:
- ✅ Workflow authenticates successfully
- ✅ Can read GCP resources
- ✅ No permission errors

---

## Phase 2: Validate Tofu Plan (Read-Only)

**Goal**: Prove `tofu plan` works without applying anything.

### Step 2.1: Create Staging Backend Config

```bash
# Already created: infra/staging.backend.hcl
cat infra/staging.backend.hcl
# Should show:
# bucket = "mindmirror-tofu-state"
# prefix = "envs/staging"
```

### Step 2.2: Initialize Tofu with New Backend

**CRITICAL**: This will create a NEW state path (`envs/staging`), separate from your current state.

```bash
cd infra

# Backup current state location
tofu init  # With old backend
tofu state pull > /tmp/old-state-backup.json

# Initialize with NEW backend (envs/staging path)
tofu init -backend-config=staging.backend.hcl -reconfigure

# Verify state is empty (fresh start)
tofu state list
# Should show: No state or empty state

# Import existing resources to new state (MANUAL, DO THIS CAREFULLY)
# We'll do this in Phase 3
```

**STOP HERE** - Don't run `tofu apply` yet!

### Step 2.3: Test Plan Workflow

Create a test branch:
```bash
git checkout -b test/wif-plan-only
git push origin test/wif-plan-only

# Create PR to staging
gh pr create \
  --base staging \
  --title "TEST: Validate tofu plan workflow" \
  --body "Testing automated planning. Will NOT merge."
```

**What to verify**:
1. `tofu-plan.yml` workflow runs
2. Authenticates via WIF successfully
3. `tofu init` works with new backend
4. `tofu plan` completes (even if shows changes)
5. Plan posted as PR comment

**Expected outcome**: Plan shows ALL resources as "to be created" (because new state is empty).

**DO NOT MERGE THIS PR YET** - Just testing the workflow.

---

## Phase 3: Import Existing State (Critical Step)

**Goal**: Move existing staging infrastructure into new state path WITHOUT changes.

### Option A: State Migration (Safest)

```bash
cd infra

# 1. Pull old state
tofu init  # Old backend
tofu state pull > /tmp/old-state.json

# 2. Initialize new backend
tofu init -backend-config=staging.backend.hcl -reconfigure

# 3. Push old state to new location
tofu state push /tmp/old-state.json

# 4. Verify state matches
tofu state list
# Should show all existing resources

# 5. Plan should show NO changes
tofu plan -var-file=staging.auto.tfvars
# Expected: "No changes. Infrastructure is up-to-date."
```

### Option B: Fresh State with Import (More Control)

If Option A doesn't work or you want more control:

```bash
cd infra
tofu init -backend-config=staging.backend.hcl -reconfigure

# Import each resource manually
# Example for agent service:
tofu import -var-file=staging.auto.tfvars \
  module.agent_service.google_cloud_run_service.agent_service \
  locations/us-east4/namespaces/mindmirror-staging/services/agent-service

# Repeat for all services...
# (This is tedious but gives you full control)
```

### Step 3.1: Verify Clean Plan

After state is imported:

```bash
cd infra
tofu init -backend-config=staging.backend.hcl
tofu plan -var-file=staging.auto.tfvars

# MUST show: "No changes. Infrastructure is up-to-date."
# If it shows changes, investigate BEFORE proceeding!
```

**Red flags**:
- ❌ Plan shows resources being destroyed
- ❌ Plan shows resources being recreated
- ❌ Plan shows unexpected attribute changes

**Fix drift before proceeding**:
```bash
# Update staging.auto.tfvars to match current reality
# Re-run plan until it's clean
```

---

## Phase 4: Test Plan Workflow (With Correct State)

Now test the plan workflow with properly imported state:

```bash
git checkout test/wif-plan-only
git pull origin test/wif-plan-only

# Make a trivial, safe change
echo "# Updated $(date)" >> infra/README.md
git add infra/README.md
git commit -m "test: trigger plan with correct state"
git push origin test/wif-plan-only
```

**Verify**:
1. Plan workflow runs
2. Plan shows "No changes" (since we only touched README)
3. No infrastructure changes proposed

**Success criteria**: Plan is clean, no proposed changes.

---

## Phase 5: Setup GitHub Environment Protection

Configure approval gates for BOTH staging and production:

### Staging Environment (Temporary Safety Gate)

1. **Repository → Settings → Environments**
2. **Create environment**: `staging`
3. **Protection rules**:
   - ✅ Required reviewers: Add yourself
   - ✅ Wait timer: 2 minutes (gives you time to cancel)
4. **Save**

### Production Environment (Permanent Safety Gate)

1. **Create environment**: `production`
2. **Protection rules**:
   - ✅ Required reviewers: Add yourself (and team)
   - ✅ Wait timer: 5 minutes
   - ✅ Deployment branches: Only `main`
3. **Save**

---

## Phase 6: Test Apply with Approval Gate

**Goal**: Run a real apply with a trivial, safe change.

### Step 6.1: Make a Safe Change

```bash
git checkout staging
git pull origin staging

# Make a truly trivial change
cd infra/modules/agent_service
# Change a description or add a tag
```

Example safe change:
```hcl
# infra/modules/agent_service/main.tf
resource "google_cloud_run_service" "agent_service" {
  name     = var.service_name
  location = var.region

  metadata {
    annotations = {
      "description" = "AI Agent Service - Updated $(date +%Y%m%d)"  # ← Safe change
    }
  }

  # ... rest unchanged
}
```

```bash
git add infra/
git commit -m "test: safe metadata change for automation testing"
git push origin staging
```

### Step 6.2: Approve and Monitor

1. **Workflow triggers** → `tofu-apply-staging.yml` starts
2. **Waits for approval** → GitHub sends notification
3. **You review**:
   - Check workflow logs
   - Verify plan shows ONLY your trivial change
   - No unexpected changes
4. **Approve deployment**
5. **Watch apply logs closely**
6. **Verify services still healthy**:
   ```bash
   gcloud run services list --project=mindmirror-staging --region=us-east4

   # Test health
   curl https://agent-service-<hash>.run.app/health
   ```

**If anything looks wrong**:
- ❌ Reject the deployment
- Investigate before trying again

---

## Phase 7: Grant Full Permissions (After Successful Test)

Once you've verified everything works:

```bash
# Grant full permissions to service account
gcloud projects add-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Remove viewer role
gcloud projects remove-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/viewer"
```

---

## Phase 8: Remove Staging Approval Gate (Optional)

Once confident, remove the approval requirement for staging:

**Edit `.github/workflows/tofu-apply-staging.yml`**:
```yaml
jobs:
  apply:
    runs-on: ubuntu-latest
    # REMOVE these lines after testing phase:
    # environment:
    #   name: staging
    #   url: https://console.cloud.google.com/run?project=mindmirror-staging
    permissions:
      contents: read
      id-token: write
      issues: write
```

**Or keep it** if you prefer manual approval for all deployments.

---

## Rollback Plan (If Things Go Wrong)

### Quick Rollback

```bash
# 1. Stop any running workflows
gh run list --workflow=tofu-apply-staging.yml
gh run cancel <RUN_ID>

# 2. Restore state from backup
cd infra
tofu init -backend-config=staging.backend.hcl
tofu state push /tmp/old-state-backup.json

# 3. Verify with plan
tofu plan -var-file=staging.auto.tfvars

# 4. If services are broken, redeploy from old state
tofu apply -var-file=staging.auto.tfvars -auto-approve
```

### Nuclear Rollback (Services Down)

```bash
# Redeploy known-good images manually
gcloud run deploy agent-service \
  --image=<KNOWN_GOOD_IMAGE> \
  --project=mindmirror-staging \
  --region=us-east4

# Repeat for each service
```

---

## Safety Checklist

**Before ANY automation runs**:
- [ ] State backed up locally
- [ ] Current service images documented
- [ ] WIF authentication tested (read-only)
- [ ] State imported correctly (clean plan)
- [ ] GitHub environments configured (staging + production)
- [ ] Rollback plan understood and tested

**Before each apply**:
- [ ] Plan reviewed thoroughly
- [ ] Only expected changes shown
- [ ] No resource deletions unless intended
- [ ] Approval gate in place
- [ ] Able to cancel if needed

**After each apply**:
- [ ] Services still healthy (curl health endpoints)
- [ ] No errors in Cloud Run logs
- [ ] State matches reality (clean plan)

---

## Recommended Testing Order

1. ✅ **Phase 0**: Backup everything
2. ✅ **Phase 1**: WIF auth test (read-only)
3. ✅ **Phase 2**: Plan workflow test (empty state)
4. ✅ **Phase 3**: Import existing state
5. ✅ **Phase 4**: Plan workflow test (correct state)
6. ✅ **Phase 5**: Setup approval gates
7. ✅ **Phase 6**: Apply workflow test (trivial change)
8. ✅ **Phase 7**: Grant full permissions
9. ✅ **Phase 8**: Remove staging approval (optional)
10. ✅ **Repeat for production**

**Timeline**:
- Phases 0-5: 1 hour (setup)
- Phase 6: 30 minutes (first real apply)
- Phases 7-8: 15 minutes (cleanup)
- **Total: ~2 hours** for bulletproof staging setup

---

## Key Safety Principles

1. **Never skip backups** - Always have a rollback point
2. **Test read before write** - Verify auth before granting apply permissions
3. **Import before apply** - Never let Tofu recreate existing resources
4. **Approval gates during testing** - Require manual review until confident
5. **One phase at a time** - Don't rush through steps
6. **Monitor everything** - Check logs, health endpoints, service status
7. **Have a rollback plan** - Know how to undo before doing

---

## What Could Go Wrong (and How to Prevent)

| Risk | Prevention | Mitigation |
|------|------------|------------|
| State corruption | Backup state before changes | Restore from backup |
| Service downtime | Approval gates, trivial changes first | Redeploy known-good images |
| WIF misconfiguration | Test read-only first | Service account keys as fallback |
| Unexpected resource changes | Import state correctly, review plans | Reject deployment, investigate |
| State lock | Monitor for stuck workflows | Force unlock via tofu CLI |
| Wrong environment | Branch-based conditions in workflows | Manual verification before approval |

---

You're now ready to test against live staging **safely**! Start with Phase 0 and work through methodically.
