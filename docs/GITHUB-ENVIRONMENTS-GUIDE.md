# GitHub Environments Explained

## What Are GitHub Environments?

GitHub Environments are **approval gates** and **secret/variable scoping** mechanisms for deployments.

Think of them as:
- 🚪 **Gates**: Manual approval checkpoints before deployment
- 🔐 **Secret Storage**: Environment-specific secrets and variables
- 🎯 **Branch Targeting**: Restrict which branches can deploy to which environments

---

## How They Work in Your Workflows

### Current Setup Analysis

You mentioned:
1. **"preview" environment** - Has all your vars, you added `GCP_PRODUCTION_PROJECT_NUM` here
2. **"production" environment** - Exists but maybe not configured?

### Workflow Integration

When a workflow references an environment:
```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://console.cloud.google.com/run?project=mindmirror-prod
```

**What happens**:
1. ✅ Workflow uses **secrets/vars from that environment** (not repo-level)
2. ✅ If environment has **protection rules**, workflow **pauses** for approval
3. ✅ Only **allowed branches** can deploy (if configured)
4. ✅ Optional **wait timer** before deployment starts

---

## Your Current Workflows

### 1. `tofu-apply-staging.yml`
```yaml
environment:
  name: staging
  url: https://console.cloud.google.com/run?project=mindmirror-69
```

**What this means**:
- When this workflow runs, it looks for a GitHub Environment named **"staging"**
- If that environment exists and has protection rules → **manual approval required**
- If that environment has secrets → uses those instead of repo-level secrets
- If environment doesn't exist → **workflow fails** (can't find environment)

### 2. `tofu-apply-production.yml`
```yaml
environment:
  name: production
  url: https://console.cloud.google.com/run?project=mindmirror-prod
```

**What this means**:
- Looks for **"production"** environment
- Typically has **required reviewers** (manual approval gate)
- Uses production-specific secrets

### 3. `tofu-plan.yml`
**No environment reference** - just reads repo-level secrets directly:
```yaml
# Uses secrets at repo level, no environment
secrets.GCP_STAGING_PROJECT_NUM
secrets.GCP_PRODUCTION_PROJECT_NUM
```

---

## Environment vs Repository Secrets

### Repository-Level Secrets (Current)
**Location**: Settings → Secrets and variables → Actions → Secrets

**Scope**: Available to ALL workflows, ALL branches

**Current secrets**:
- `GCP_STAGING_PROJECT_NUM` (you need to add this)
- `GCP_PRODUCTION_PROJECT_NUM` (you need to add this)

**Used by**: `tofu-plan.yml` (reads both to detect environment)

### Environment-Level Secrets/Variables
**Location**: Settings → Environments → [environment name] → Environment secrets/variables

**Scope**: Only available when workflow uses that specific environment

**Example**:
```
Environment: "production"
├─ Secrets:
│  └─ DEPLOY_KEY (production-specific)
├─ Variables:
│  └─ ENVIRONMENT_NAME = "production"
└─ Protection rules:
   └─ Required reviewers: [peleke]
```

---

## Your Setup Strategy (Recommended)

### Option 1: Use Repository Secrets + Environment Protection (Simpler)

**Repository secrets** (accessible to all workflows):
```
GCP_STAGING_PROJECT_NUM = "3858903851"
GCP_PRODUCTION_PROJECT_NUM = "[production project number]"
```

**GitHub Environments** (for approval gates only):

#### "staging" Environment
- **Purpose**: Approval gate for staging deployments (during testing phase)
- **Protection rules**:
  - ✅ Required reviewers: You
  - ⏰ Wait timer: 0 minutes (no delay)
  - 🌿 Deployment branches: Only `staging` branch
- **Secrets/Variables**: None needed (uses repo secrets)

#### "production" Environment
- **Purpose**: Approval gate for production deployments (permanent)
- **Protection rules**:
  - ✅ Required reviewers: You (+ team members)
  - ⏰ Wait timer: 5 minutes (safety delay)
  - 🌿 Deployment branches: Only `main` branch
- **Secrets/Variables**: None needed (uses repo secrets)

**When to use this**: You want simple approval gates, secrets are not environment-specific.

---

### Option 2: Environment-Specific Secrets (More Isolation)

**Repository secrets** (minimal):
```
# Maybe nothing, or just GitHub-specific stuff
```

**"staging" Environment**:
```
Secrets:
├─ GCP_STAGING_PROJECT_NUM = "3858903851"

Variables:
└─ ENVIRONMENT = "staging"

Protection rules:
└─ Required reviewers: You (temporary, remove later)
```

**"production" Environment**:
```
Secrets:
├─ GCP_PRODUCTION_PROJECT_NUM = "[prod project number]"

Variables:
└─ ENVIRONMENT = "production"

Protection rules:
└─ Required reviewers: You + team (permanent)
```

**When to use this**: You want complete secret isolation between environments.

---

## Your Current Situation

You mentioned a **"preview" environment** with vars and `GCP_PRODUCTION_PROJECT_NUM`.

### Issue 1: Name Mismatch
Your workflows reference:
- `environment: staging`
- `environment: production`

But you have:
- "preview" environment (not referenced by any workflow)
- "production" environment

**Problem**: `tofu-apply-staging.yml` looks for "staging" environment, but you only have "preview".

### Issue 2: Where Did You Put `GCP_PRODUCTION_PROJECT_NUM`?

If you put it in the **"preview" environment**:
- ❌ `tofu-plan.yml` **can't see it** (plan workflow doesn't use environment)
- ❌ `tofu-apply-staging.yml` **can't see it** (looks for "staging", not "preview")

If you put it as a **repository secret**:
- ✅ All workflows can see it
- ✅ This is correct!

---

## What You Need to Do

### Quick Fix (Recommended):

**1. Add repository secrets** (not environment secrets):
```bash
# Go to: Settings → Secrets and variables → Actions → Repository secrets
# Add:
GCP_STAGING_PROJECT_NUM = 3858903851
GCP_PRODUCTION_PROJECT_NUM = [your production project number from bootstrap]
```

**2. Create/update GitHub Environments**:

**Option A: Keep it simple (approval gates only)**
```
Create "staging" environment:
- Settings → Environments → New environment → "staging"
- Required reviewers: Add yourself
- Deployment branches: staging
- No secrets/variables needed (uses repo secrets)

Update "production" environment:
- Required reviewers: Add yourself (and team)
- Deployment branches: main
- No secrets/variables needed (uses repo secrets)
```

**Option B: Full isolation (environment-specific secrets)**
```
"staging" environment:
- Required reviewers: You
- Environment secrets:
  - GCP_STAGING_PROJECT_NUM = 3858903851
- Deployment branches: staging

"production" environment:
- Required reviewers: You + team
- Environment secrets:
  - GCP_PRODUCTION_PROJECT_NUM = [prod number]
- Deployment branches: main
```

**3. Update workflows if using Option B**:

For `tofu-plan.yml` (if using environment secrets):
```yaml
# This currently reads repo secrets directly
# If using environment secrets, it needs to know which environment to read from
# This gets complex, so Option A is simpler
```

---

## Approval Gate Flow (How It Works)

### Scenario: You Push to `staging` Branch

**Step 1**: Code pushed to `staging` branch
```
git push origin staging
```

**Step 2**: `tofu-apply-staging.yml` workflow triggered
```yaml
on:
  push:
    branches:
      - staging
```

**Step 3**: Workflow reaches environment block
```yaml
jobs:
  apply:
    environment:
      name: staging  # ← Looks for "staging" environment
```

**Step 4**: GitHub checks environment "staging"
- Does it exist? ✅ Yes
- Does it have required reviewers? ✅ Yes (you)
- **Workflow PAUSES** and shows notification

**Step 5**: You get notification
```
🔔 Deployment to staging is waiting for your review
```

**Step 6**: You review and approve
- Go to: Actions → [workflow run] → Review deployments → Approve

**Step 7**: Workflow continues
- Runs `tofu apply`
- Deploys to staging

**Step 8**: Workflow completes
- Success or failure status posted

---

## Why Use Environments?

### ✅ Benefits:

1. **Manual Approval Gates**
   - Prevent accidental production deploys
   - Give you time to review changes
   - Require team sign-off

2. **Secret Scoping**
   - Production secrets only available to production deployments
   - Staging can't access production secrets

3. **Audit Trail**
   - See who approved each deployment
   - Track deployment history per environment

4. **Branch Protection**
   - Only `main` can deploy to production
   - Only `staging` can deploy to staging
   - Prevent accidental deploys from feature branches

### ❌ When NOT to Use:

1. **CI/CD for Pull Requests**
   - PRs should run without approval (automated testing)
   - Use environments only for actual deployments

2. **Simple Projects**
   - If you're solo and don't need gates, skip it
   - Repo-level secrets are simpler

---

## Your "preview" Environment Confusion

### What is "preview"?

**Typical use case**: Preview deployments for PRs
```yaml
# Preview deployment workflow (optional)
on:
  pull_request:

jobs:
  preview:
    environment:
      name: preview  # Temporary deployment for this PR
      url: https://pr-${{ github.event.number }}-preview.run.app
```

**Example**: Vercel/Netlify-style preview deployments
- Each PR gets its own temporary environment
- URL: `https://pr-123-mindmirror.vercel.app`

### Do You Need "preview"?

For your setup, probably **NO**:
- You're using `-auto` parallel stack for testing (that's your "preview")
- Your workflows only reference "staging" and "production"
- "preview" is unused

**Recommendation**: Delete "preview" environment or rename it to "staging".

---

## Final Recommendations

### For Your Current Setup:

**1. Repository Secrets (Quick)**:
```
Settings → Secrets → Repository secrets → Add:
- GCP_STAGING_PROJECT_NUM = 3858903851
- GCP_PRODUCTION_PROJECT_NUM = [from bootstrap]
```

**2. Create "staging" Environment**:
```
Settings → Environments → New → "staging"
Protection rules:
- Required reviewers: peleke
- Deployment branches: staging
```

**3. Update "production" Environment**:
```
Settings → Environments → production
Protection rules:
- Required reviewers: peleke (+ future team members)
- Deployment branches: main
- Wait timer: 5 minutes (optional safety delay)
```

**4. Delete "preview" Environment** (if unused):
```
Settings → Environments → preview → Delete
```

**5. Test the Flow**:
```bash
# Create test branch
git checkout -b test/approval-gate
echo "# test" >> infra/README.md
git add infra/README.md
git commit -m "test: trigger staging approval gate"
git push origin test/approval-gate

# Create PR to staging
gh pr create --base staging --title "TEST: Approval gate" --body "Testing manual approval"

# Merge PR → workflow pauses for your approval
# Go to Actions → Review deployment → Approve
```

---

## Quick Reference

### Check Current Environments
```
Settings → Environments
```

### Check Repository Secrets
```
Settings → Secrets and variables → Actions → Secrets
```

### View Workflow Runs Waiting for Approval
```
Actions → [workflow name] → [run] → "Review deployments" button
```

### Approve Pending Deployment
```
Actions → [waiting workflow] → Review deployments → Approve
```

### Environment Protection Rule Options
- ✅ **Required reviewers**: Who must approve (1-6 people)
- ⏰ **Wait timer**: Delay before deployment (0-43200 minutes)
- 🌿 **Deployment branches**: Which branches can deploy (selected branches, protected branches, all branches)

---

## Summary

**GitHub Environments** = Approval gates + Secret scoping

**Your workflows**:
- `tofu-plan.yml`: No environment (uses repo secrets)
- `tofu-apply-staging.yml`: Uses "staging" environment (needs approval if configured)
- `tofu-apply-production.yml`: Uses "production" environment (needs approval)

**Your task**:
1. Add `GCP_STAGING_PROJECT_NUM` and `GCP_PRODUCTION_PROJECT_NUM` as **repository secrets**
2. Create "staging" environment with approval gate
3. Configure "production" environment with approval gate
4. Delete "preview" if unused
5. Test by creating a PR to staging branch

**Result**: Manual approval required for all staging and production deployments, no accidental deploys!
