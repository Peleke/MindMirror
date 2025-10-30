# GitHub Actions Deployment Guide

**Pure GitHub Actions approach** for automated infrastructure deployment with OpenTofu.

**Timeline**: 1 hour setup → Production ready
**Cost**: $0 (uses existing GCS backend)
**Dependencies**: None (no Terrateam, Atlantis, or external services)

## Key Updates (Latest)

✅ **Automated WIF Setup**: One-command script creates service accounts + WIF pool + bindings
✅ **WIF Testing Workflow**: Test authentication BEFORE touching infrastructure (zero-risk validation)
✅ **Staging Approval Gates**: Both staging and production require manual approval (safe parallel testing)
✅ **Correct Project IDs**: `mindmirror-69` = staging, `mindmirror-prod` = production
✅ **Parallel Stack Ready**: Deploys `-auto` services for safe testing alongside production

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Developer Workflow                                       │
│                                                          │
│  1. Test WIF (Actions → test-wif-auth.yml)              │
│  2. Feature branch → PR to staging/main                 │
│  3. tofu-plan.yml runs → Comments plan on PR            │
│  4. Review plan → Merge PR                              │
│  5. Manual approval required (both staging + production)│
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ GitHub Actions Workflows                                 │
│                                                          │
│  test-wif-auth.yml          → Manual trigger (critical) │
│    ├─ Authenticate via WIF                              │
│    ├─ Test GCP access (read-only)                       │
│    └─ Validate before infrastructure changes            │
│                                                          │
│  tofu-plan.yml              → Runs on PR                │
│    ├─ Detects environment (staging/production)          │
│    ├─ tofu plan                                         │
│    └─ Comments plan on PR                               │
│                                                          │
│  tofu-apply-staging.yml     → Runs on merge to staging  │
│    ├─ Requires manual approval (GitHub Environment)     │
│    ├─ tofu init + plan                                  │
│    ├─ tofu apply -auto-approve                          │
│    └─ Verify deployment (-auto services)                │
│                                                          │
│  tofu-apply-production.yml  → Runs on merge to main     │
│    ├─ Requires manual approval (GitHub Environment)     │
│    ├─ tofu init + plan                                  │
│    ├─ tofu apply -auto-approve                          │
│    ├─ Verify deployment                                 │
│    └─ Create deployment issue (success/failure)         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ State Storage                                            │
│                                                          │
│  GCS Bucket: mindmirror-tofu-state                      │
│    ├─ envs/staging/    (staging state)                  │
│    └─ envs/production/ (production state)               │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: Setup Workload Identity Federation (5 minutes)

**Automated Setup** (Recommended):

```bash
# Run the WIF bootstrap script
cd infra-v2/bootstrap
./06-bootstrap-wif.sh
```

This script automatically:
- ✅ Creates `github-actions-staging` service account (if missing)
- ✅ Grants necessary IAM roles (run.admin, storage.admin, secretmanager.admin, etc.)
- ✅ Creates WIF pool and OIDC provider (if not exists)
- ✅ Binds service account to WIF pool
- ✅ Displays project number for GitHub secrets

**Output example**:
```
Configuration:
  • Service Account: github-actions-staging@mindmirror-69.iam.gserviceaccount.com
  • WIF Pool: github-pool
  • WIF Provider: github-oidc
  • GitHub Repo: Peleke/MindMirror

Next steps:
  1. Add these secrets to your GitHub repository:
     - GCP_STAGING_PROJECT_NUM: 3858903851
     - GCP_PRODUCTION_PROJECT_NUM: (from production bootstrap)
```

**Manual Setup** (if needed):
See `infra-v2/bootstrap/06-bootstrap-wif.sh` for individual commands

---

## Phase 2: Configure GitHub Secrets (5 minutes)

**Add these secrets** to your repository:

1. Go to: Repository → Settings → Secrets and variables → Actions → Secrets
2. Click "New repository secret"
3. Add:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `GCP_STAGING_PROJECT_NUM` | `3858903851` | `gcloud projects describe mindmirror-69 --format='value(projectNumber)'` |
| `GCP_PRODUCTION_PROJECT_NUM` | Your production project number | `gcloud projects describe mindmirror-prod --format='value(projectNumber)'` |

**Important**:
- ✅ These are **project numbers** (e.g., `3858903851`), NOT project IDs
- ✅ Staging project: `mindmirror-69` (numerical ID: `3858903851`)
- ✅ Production project: `mindmirror-prod` (get number from bootstrap output)

---

## Phase 3: Setup GitHub Environment Protection (10 minutes)

Configure manual approval gates for **both staging and production** deployments.

**Why approval gates for staging?**
- ✅ Safe testing of parallel stack (`-auto` services) alongside production
- ✅ Prevents accidental infrastructure changes during development
- ✅ Can be removed later once parallel stack is validated

### Create Staging Environment

1. **Go to**: Repository → Settings → Environments
2. **Click**: "New environment"
3. **Name**: `staging`
4. **Configure protection rules**:
   - ✅ Required reviewers: Add yourself
   - ⏰ Wait timer: 0 minutes (no delay during testing)
   - 🌿 Deployment branches: Only `staging` branch
5. **Save**

### Create Production Environment

1. **Click**: "New environment" again
2. **Name**: `production`
3. **Configure protection rules**:
   - ✅ Required reviewers: Add yourself (and team members)
   - ⏰ Wait timer: 5 minutes (optional safety delay)
   - 🌿 Deployment branches: Only `main` branch
4. **Save**

**Result**: Both environments require manual approval before infrastructure changes are applied.

**See**: `docs/GITHUB-ENVIRONMENTS-GUIDE.md` for detailed explanation of GitHub Environments.

---

## Phase 4: Verify Workflows Exist (1 minute)

All workflow files should already exist (created by this guide):

```bash
ls -la .github/workflows/tofu-*

# Should see:
# .github/workflows/tofu-plan.yml
# .github/workflows/tofu-apply-staging.yml
# .github/workflows/tofu-apply-production.yml
```

Backend configs:
```bash
ls -la infra/*.backend.hcl

# Should see:
# infra/staging.backend.hcl
# infra/production.backend.hcl
```

---

## Phase 4.5: Test WIF Authentication (10 minutes) ⚡ CRITICAL

**Test WIF BEFORE touching infrastructure** to ensure authentication works.

### Why Test WIF First?

- ✅ Validates WIF configuration without infrastructure changes
- ✅ Catches authentication issues early
- ✅ Verifies GitHub secrets are correct
- ✅ Zero risk (read-only operations)

### Run WIF Test Workflow

1. **Go to**: Repository → Actions → "Test WIF Authentication"
2. **Click**: "Run workflow"
3. **Select**: `staging` environment
4. **Click**: "Run workflow" button

### What Gets Tested

```bash
✅ Authenticate to GCP via WIF
✅ Describe GCP project
✅ List Cloud Run services
✅ List service accounts
✅ List secrets (may fail if no permission - expected)
✅ Display WIF configuration details
```

### Expected Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WIF Authentication Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment: staging
Project: mindmirror-69

✅ Authentication successful!
✅ Can access GCP resources
✅ WIF configuration working

Next steps:
  1. Grant additional permissions if needed
  2. Test tofu plan workflow
  3. Setup GitHub Environment protection
```

### If Test Fails

**Common errors**:

1. **"Failed to generate Google Cloud access token"**
   - ❌ Check `GCP_STAGING_PROJECT_NUM` secret is correct
   - ❌ Verify WIF pool and provider exist: `gcloud iam workload-identity-pools list`
   - ❌ Check service account binding

2. **"Permission denied"**
   - ❌ Service account missing roles
   - ❌ Re-run `./06-bootstrap-wif.sh` to grant roles

3. **"Unknown service account"**
   - ❌ Service account doesn't exist
   - ❌ Re-run `./06-bootstrap-wif.sh` to create it

### Test Production WIF (Optional)

Repeat the test for production:
```
1. Actions → "Test WIF Authentication" → Run workflow
2. Select: production
3. Verify authentication works
```

**Once WIF test passes**, proceed to infrastructure deployment testing.

---

## Phase 5: Test Staging Deployment (30 minutes)

### Step 1: Create Test PR to Staging

```bash
# Create test branch
git checkout -b test/tofu-automation
git push origin test/tofu-automation

# Make a trivial infra change
cd infra
echo "# Test automated deployment" >> README.md
git add README.md
git commit -m "test: verify tofu automation"
git push origin test/tofu-automation

# Create PR targeting staging branch
gh pr create --base staging --title "Test: Tofu automation" --body "Testing automated infrastructure deployment"
```

### Step 2: Watch tofu-plan.yml Run

1. Go to: Repository → Pull Requests → Your PR
2. Wait 1-2 minutes for `tofu-plan.yml` to run
3. **Verify**:
   - ✅ Workflow runs successfully
   - ✅ Bot comments plan on PR
   - ✅ Plan shows expected changes (or "No changes")

### Step 3: Merge PR → Auto-Apply

```bash
# Merge the PR
gh pr merge --squash

# Or via GitHub UI
```

**Watch the magic**:
1. Go to: Actions → "Tofu Apply - Staging"
2. Watch workflow:
   - Runs `tofu init` with staging backend
   - Runs `tofu plan`
   - Runs `tofu apply -auto-approve` (no manual approval needed)
   - Verifies deployment by listing Cloud Run services
3. **Verify success**:
   ```bash
   gcloud run services list --project=mindmirror-69 --region=us-east4
   ```

---

## Phase 6: Test Production Deployment (30 minutes)

### Step 1: Create PR to Main

```bash
# Checkout main, merge staging
git checkout main
git pull origin main
git merge staging --no-ff -m "chore: merge staging to main for production test"
git push origin main
```

**Or** make a direct change:
```bash
git checkout -b test/production-deploy
# Make infra change
git add infra/
git commit -m "test: production deployment automation"
git push origin test/production-deploy

gh pr create --base main --title "Test: Production deployment" --body "Testing production deployment automation"
```

### Step 2: Review Plan on PR

1. Go to PR
2. Wait for `tofu-plan.yml` to comment
3. **Carefully review** the plan:
   - ✅ Only expected resources changing
   - ✅ No unexpected deletions/replacements
   - ✅ Image tags correct

### Step 3: Merge PR → Manual Approval Required

```bash
gh pr merge --squash
```

**What happens**:
1. Merge triggers `tofu-apply-production.yml`
2. Workflow waits for manual approval (GitHub Environment protection)
3. **You see**: "Waiting for approval" in Actions tab
4. **GitHub sends notification**: Review deployment request

### Step 4: Approve Production Deployment

1. Go to: Actions → "Tofu Apply - Production" → Current run
2. Click: **"Review deployments"** button
3. Select: `production` environment
4. Click: **"Approve and deploy"**

**Watch the deployment**:
- Tofu init + plan
- Pre-flight checklist
- Tofu apply
- Service verification
- Deployment issue created

### Step 5: Verify Production

```bash
# Check services
gcloud run services list --project=mindmirror-prod --region=us-east4

# Test health endpoint
AGENT_URL=$(gcloud run services describe agent-service \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format='value(status.url)')

curl $AGENT_URL/health
```

---

## Daily Workflow

### Deploying to Staging

```bash
# 1. Work on feature branch
git checkout -b feature/my-feature

# 2. Make changes (code or infra)
# ... edit files ...

# 3. Create PR to staging
git push origin feature/my-feature
gh pr create --base staging --title "feat: my feature"

# 4. Review auto-generated plan on PR

# 5. Merge PR
gh pr merge --squash

# 6. Approve deployment in GitHub Actions UI
# → Go to Actions → Review deployments → Approve

# → Deploys to -auto parallel stack in 2-3 minutes
```

**Note**: Staging approval gate is temporary during parallel stack testing. Can be removed later.

### Deploying to Production

```bash
# 1. Merge staging to main (or cherry-pick commits)
git checkout main
git merge staging --no-ff
git push origin main

# 2. Review plan comment on auto-created PR (or existing PR)

# 3. Merge PR
gh pr merge --squash

# 4. Approve deployment in GitHub Actions UI
# → Go to Actions → Review deployments → Approve

# 5. Verify deployment via auto-created issue
# → Check Issues tab for "✅ Production deployment: <sha>"
```

### Updating Infrastructure Only

```bash
# If only changing infra/ files:
git checkout -b infra/update-service-config
cd infra/modules/agent_service
# ... make changes ...
git add infra/
git commit -m "chore(infra): update agent service config"
git push origin infra/update-service-config

# Create PR → Plan runs → Review → Merge → Deploy
gh pr create --base staging
```

---

## Troubleshooting

### Plan Workflow Not Running

**Check**:
- PR targets `staging` or `main` branch?
- PR touches `infra/**` files?
- Workflow file syntax valid?

**Fix**:
```bash
# Manually trigger via workflow_dispatch (if enabled)
# Or push a trivial change to infra/
echo "# trigger" >> infra/README.md
git add infra/README.md
git commit -m "chore: trigger plan"
git push
```

### WIF Authentication Fails

**Error**: "Failed to generate Google Cloud access token"

**Check**:
1. Workflow has `permissions.id-token: write`?
2. WIF provider exists?
3. Service account binding correct?
4. Project number secrets configured?

**Verify**:
```bash
# Check WIF pool
gcloud iam workload-identity-pools describe github-pool \
  --project=PROJECT_ID \
  --location=global

# Check service account bindings
gcloud iam service-accounts get-iam-policy \
  github-actions-staging@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID
```

### Apply Fails - State Lock

**Error**: "Error acquiring state lock"

**Cause**: Previous workflow interrupted or failed

**Fix**:
```bash
# Manual state unlock
cd infra
tofu init -backend-config=staging.backend.hcl
tofu force-unlock <LOCK_ID>  # Get LOCK_ID from error message
```

### Production Approval Not Showing

**Check**:
- GitHub Environment `production` exists?
- You're listed as required reviewer?
- Workflow references correct environment name?

**Fix**:
```bash
# Re-create environment
# Settings → Environments → Delete "production" → Create new
```

### Plan Shows Unexpected Changes

**Common causes**:
- Drift: Manual changes in GCP Console
- Wrong tfvars file
- State out of sync

**Investigation**:
```bash
# Check what's in state
cd infra
tofu init -backend-config=staging.backend.hcl
tofu show

# Refresh state
tofu refresh -var-file=staging.auto.tfvars

# Re-plan
tofu plan -var-file=staging.auto.tfvars
```

---

## Advanced Features

### Add Cost Estimation (Optional)

Install Infracost action to PR comments:

```yaml
# Add to tofu-plan.yml after plan step
- name: Setup Infracost
  uses: infracost/actions/setup@v2
  with:
    api-key: ${{ secrets.INFRACOST_API_KEY }}

- name: Generate cost estimate
  run: |
    infracost breakdown --path infra \
      --terraform-var-file ${{ env.ENVIRONMENT }}.auto.tfvars \
      --format json --out-file /tmp/infracost.json

- name: Post cost comment
  run: |
    infracost comment github --path /tmp/infracost.json \
      --repo $GITHUB_REPOSITORY \
      --pull-request ${{ github.event.pull_request.number }}
```

### Add Drift Detection (Optional)

Scheduled workflow to detect configuration drift:

```yaml
# .github/workflows/tofu-drift-detection.yml
name: Tofu Drift Detection
on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM UTC

jobs:
  detect-drift:
    # ... similar to plan workflow
    # Run tofu plan -detailed-exitcode
    # Create issue if drift detected
```

### Add Policy Checks (Optional)

Use Open Policy Agent (OPA) for policy enforcement:

```yaml
# Add to plan workflow before apply
- name: OPA Policy Check
  run: |
    opa test policies/
    tofu show -json plan.tfplan > plan.json
    opa eval -d policies/ -i plan.json "data.terraform.deny"
```

---

## Comparison: GitHub Actions vs Terrateam

| Feature | GitHub Actions | Terrateam |
|---------|---------------|-----------|
| **Cost** | Free | Free (hosted) |
| **Setup Time** | 2 hours | 30 minutes |
| **Dependencies** | None | Terrateam service |
| **Customization** | Full control | Limited to config |
| **PR Comments** | ✅ Via github-script | ✅ Built-in |
| **Manual Approval** | ✅ GitHub Environments | ✅ Comment-based |
| **State Management** | GCS backend | GCS backend |
| **Reliability** | GitHub uptime | Terrateam + GitHub |
| **Learning Curve** | Moderate (YAML) | Low (config file) |
| **Vendor Lock-in** | GitHub only | Terrateam + GitHub |

---

## What You've Automated

✅ **Infrastructure planning**: Auto-plan on PR with PR comments
✅ **WIF testing**: Validate authentication without infrastructure changes
✅ **Staging deploys**: Manual approval (during parallel stack testing)
✅ **Production deploys**: Manual approval required (permanent)
✅ **Deployment verification**: Auto-check service health
✅ **Deployment tracking**: Auto-created issues for success/failure
✅ **State management**: Isolated per environment (GCS)
✅ **Security**: WIF keyless authentication (no service account keys!)
✅ **Audit trail**: Full history in GitHub Actions
✅ **Parallel stack safety**: `-auto` suffix services for safe testing

---

## Next Steps

**Critical Path** (do in order):

1. ✅ **Run WIF bootstrap script**: `cd infra-v2/bootstrap && ./06-bootstrap-wif.sh`
2. ✅ **Configure GitHub secrets**: Add `GCP_STAGING_PROJECT_NUM` and `GCP_PRODUCTION_PROJECT_NUM`
3. ✅ **Setup GitHub environments**: Create `staging` and `production` with approval gates
4. ✅ **Test WIF authentication**: Run `test-wif-auth.yml` workflow (BEFORE infrastructure changes!)
5. ✅ **Test tofu plan**: Create PR to staging, verify plan comments work
6. ✅ **Test staging deployment**: Merge PR, approve deployment, verify `-auto` services created
7. ✅ **Validate parallel stack**: Test `-auto` services, confirm no impact to production
8. ✅ **Test production deployment**: PR to main, approve, verify production services

**Optional Enhancements**:

9. **Cost estimation**: Add Infracost to plan comments
10. **Drift detection**: Scheduled workflow to detect manual changes
11. **Policy checks**: OPA for infrastructure compliance
12. **Remove staging approval**: Once parallel stack validated, remove staging environment protection

---

## Migration from Terrateam

If migrating from Terrateam:

1. **Keep existing state** - No migration needed (same GCS backend)
2. **Remove Terrateam config** - Delete `.terrateam/config.yml`
3. **Uninstall Terrateam GitHub App** - Settings → GitHub Apps
4. **Test new workflows** - Start with staging
5. **Update documentation** - Point team to new workflow

**Rollback plan**: Keep Terrateam config in a branch for easy revert if needed.
