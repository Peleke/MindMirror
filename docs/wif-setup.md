# Workload Identity Federation Setup Guide

**Goal**: Replace service account keys with keyless authentication from GitHub Actions to GCP
**Security Benefit**: Eliminate long-lived credentials, auto-expiring tokens (1 hour), fine-grained access control
**Timeline**: 2-3 hours setup per environment (staging + production)

---

## Why Workload Identity Federation?

### Current Approach (Service Account Keys) ❌
```yaml
# GitHub Secrets contain long-lived JSON keys
secrets.GCP_STAGING_SA_KEY    # Lives forever, high-value target
secrets.GCP_PRODUCTION_SA_KEY # Lives forever, high-value target

# Workflow uses keys directly
- uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_STAGING_SA_KEY }}
```

**Problems**:
- Keys never expire (must be rotated manually)
- Keys stored in GitHub Secrets (single point of compromise)
- Broad permissions (keys grant full SA permissions)
- Key leakage risk (logs, env dumps, debugging)
- Compliance issues (SOC2, PCI, HIPAA)

### Workload Identity Federation Approach ✅
```yaml
# NO secrets stored in GitHub
# Workflow uses OIDC tokens from GitHub

- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123/locations/global/workloadIdentityPools/github/providers/github-oidc'
    service_account: 'github-actions-staging@PROJECT.iam.gserviceaccount.com'
```

**Benefits**:
- ✅ No long-lived secrets (GitHub issues OIDC tokens dynamically)
- ✅ Tokens auto-expire after 1 hour
- ✅ Fine-grained access control (limit by repo, branch, username)
- ✅ Audit trail (see which repo/branch triggered action)
- ✅ Zero secret management (no rotation, no storage)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions Workflow (staging-deploy.yml)                │
│                                                              │
│ 1. Workflow triggers on push to 'staging' branch            │
│ 2. GitHub generates OIDC token with claims:                 │
│    - repository: "your-org/MindMirror"                      │
│    - ref: "refs/heads/staging"                              │
│    - actor: "username"                                      │
│    - workflow: "Deploy to Staging"                          │
└─────────────────┬────────────────────────────────────────────┘
                  │
                  │ OIDC Token (JWT)
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ GCP Workload Identity Pool (github-pool)                    │
│                                                              │
│ Provider: github-oidc                                       │
│ Issuer: https://token.actions.githubusercontent.com         │
│                                                              │
│ Attribute Mapping (CEL):                                    │
│ - google.subject = assertion.sub                            │
│ - attribute.repository = assertion.repository               │
│ - attribute.actor = assertion.actor                         │
│ - attribute.ref = assertion.ref                             │
└─────────────────┬────────────────────────────────────────────┘
                  │
                  │ Validates token, extracts attributes
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Service Account (github-actions-staging)                    │
│                                                              │
│ IAM Binding:                                                │
│ - Role: roles/iam.workloadIdentityUser                      │
│ - Member: principalSet://...repository/your-org/MindMirror  │
│                                                              │
│ Condition (optional):                                       │
│ - assertion.ref == "refs/heads/staging"                     │
└─────────────────┬────────────────────────────────────────────┘
                  │
                  │ Impersonates SA, grants short-lived token
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ GCP Resources (Artifact Registry, Cloud Run, etc.)          │
│                                                              │
│ Workflow authenticated as:                                  │
│ github-actions-staging@PROJECT.iam.gserviceaccount.com      │
│                                                              │
│ Token valid for: 1 hour                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Setup Steps

### Prerequisites
- GitHub repository: `your-org/MindMirror`
- GCP projects: `mindmirror-staging`, `mindmirror-69` (production)
- Service accounts already created (from Terrateam setup)
- GitHub Actions workflows already exist (from Terrateam setup)

---

## Phase 1: Staging Environment Setup

### Step 1: Create Workload Identity Pool (Staging)

```bash
export STAGING_PROJECT="mindmirror-staging"
export STAGING_PROJECT_NUM=$(gcloud projects describe $STAGING_PROJECT --format='value(projectNumber)')

# Create workload identity pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Verify pool created
gcloud iam workload-identity-pools describe "github-pool" \
  --project="${STAGING_PROJECT}" \
  --location="global"
```

**Output**: Pool resource name like:
```
projects/123456789/locations/global/workloadIdentityPools/github-pool
```

---

### Step 2: Create OIDC Provider for GitHub

```bash
# Create GitHub OIDC provider in the pool
gcloud iam workload-identity-pools providers create-oidc "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository_owner == 'your-org'"

# Verify provider created
gcloud iam workload-identity-pools providers describe "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool"
```

**Important**: Replace `'your-org'` with your actual GitHub organization name (e.g., `'swae'`)

**Attribute Mapping Explanation**:
- `google.subject`: Unique identifier for the GitHub Actions workflow
- `attribute.actor`: GitHub username who triggered the workflow
- `attribute.repository`: Full repo name (e.g., `swae/MindMirror`)
- `attribute.repository_owner`: GitHub org/user (e.g., `swae`)
- `attribute.ref`: Git ref (e.g., `refs/heads/staging`)

**Attribute Condition**: Only allow tokens from your organization (prevents other GitHub users from using your pool)

---

### Step 3: Bind Service Account to Pool (Staging)

```bash
export STAGING_SA="github-actions-staging@${STAGING_PROJECT}.iam.gserviceaccount.com"

# Grant Workload Identity User role to the pool for this specific repo
gcloud iam service-accounts add-iam-policy-binding "${STAGING_SA}" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror"

# Add additional condition to restrict to 'staging' branch only
gcloud iam service-accounts add-iam-policy-binding "${STAGING_SA}" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror" \
  --condition='expression=assertion.ref == "refs/heads/staging",title=staging-branch-only,description=Only allow staging branch'
```

**Important**:
- Replace `your-org/MindMirror` with your actual repo (e.g., `swae/MindMirror`)
- The condition ensures only pushes to `staging` branch can use this SA

**Verify Binding**:
```bash
gcloud iam service-accounts get-iam-policy "${STAGING_SA}" \
  --project="${STAGING_PROJECT}"
```

---

### Step 4: Get Workload Identity Provider Resource Name

```bash
# Get the full provider resource name for GitHub Actions workflow
gcloud iam workload-identity-pools providers describe "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"
```

**Example Output**:
```
projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-oidc
```

**Save this**: You'll need it in the GitHub Actions workflow

---

### Step 5: Update GitHub Actions Workflow (Staging)

Edit `.github/workflows/staging-deploy.yml`:

**Before (using SA keys)**:
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_STAGING_SA_KEY }}  # ❌ Old approach
```

**After (using WIF)**:
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-oidc'
    service_account: 'github-actions-staging@mindmirror-staging.iam.gserviceaccount.com'
```

**Full Updated Job**:
```yaml
build-and-push:
  name: Build ${{ matrix.service }}
  runs-on: ubuntu-latest
  needs: detect-changes
  if: needs.detect-changes.outputs.has_changes == 'true'

  # IMPORTANT: Request OIDC token from GitHub
  permissions:
    contents: read
    id-token: write  # Required for OIDC token generation

  strategy:
    fail-fast: false
    matrix:
      service: ${{ fromJson(needs.detect-changes.outputs.services) }}
      exclude:
        - service: web_app
        - service: mobile_app

  steps:
    - uses: actions/checkout@v4

    # NEW: WIF-based authentication
    - name: Authenticate to Google Cloud (Staging)
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-oidc'
        service_account: 'github-actions-staging@mindmirror-staging.iam.gserviceaccount.com'

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2

    # Rest of workflow stays the same...
```

**Critical Changes**:
1. Add `permissions.id-token: write` to job (enables OIDC token request)
2. Replace `credentials_json` with `workload_identity_provider` + `service_account`
3. Remove `secrets.GCP_STAGING_SA_KEY` reference

---

### Step 6: Test Staging Workflow

```bash
# Commit and push changes
git checkout staging
git add .github/workflows/staging-deploy.yml
git commit -m "feat: switch to Workload Identity Federation for staging"
git push origin staging

# Monitor GitHub Actions
# → Go to https://github.com/your-org/MindMirror/actions
# → Check "Deploy to Staging" workflow
# → Verify authentication succeeds (no more SA key warnings)
```

**Success Indicators**:
- ✅ Workflow authenticates without errors
- ✅ Can push images to Artifact Registry
- ✅ No `GCP_STAGING_SA_KEY` secret used
- ✅ GitHub Actions logs show: "Successfully authenticated to Google Cloud"

**If Authentication Fails**:
1. Check `permissions.id-token: write` is set
2. Verify workload identity provider path is correct
3. Verify service account email is correct
4. Check IAM binding: `gcloud iam service-accounts get-iam-policy ...`
5. Verify attribute condition matches (repo name, branch name)

---

## Phase 2: Production Environment Setup

**Repeat Phase 1 steps for production, with these changes**:

### Step 1: Create Workload Identity Pool (Production)

```bash
export PROD_PROJECT="mindmirror-69"
export PROD_PROJECT_NUM=$(gcloud projects describe $PROD_PROJECT --format='value(projectNumber)')

gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROD_PROJECT}" \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

### Step 2: Create OIDC Provider (Production)

```bash
gcloud iam workload-identity-pools providers create-oidc "github-oidc" \
  --project="${PROD_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository_owner == 'your-org'"
```

### Step 3: Bind Service Account to Pool (Production)

```bash
export PROD_SA="github-actions-prod@${PROD_PROJECT}.iam.gserviceaccount.com"

# Grant WIF permission
gcloud iam service-accounts add-iam-policy-binding "${PROD_SA}" \
  --project="${PROD_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROD_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror"

# Add condition to restrict to 'main' branch only
gcloud iam service-accounts add-iam-policy-binding "${PROD_SA}" \
  --project="${PROD_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROD_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror" \
  --condition='expression=assertion.ref == "refs/heads/main",title=main-branch-only,description=Only allow main branch'
```

### Step 4: Get Provider Resource Name (Production)

```bash
gcloud iam workload-identity-pools providers describe "github-oidc" \
  --project="${PROD_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"
```

### Step 5: Update Production Workflow

Edit `.github/workflows/production-deploy.yml`:

```yaml
build-and-push:
  name: Build ${{ matrix.service }}
  runs-on: ubuntu-latest
  needs: detect-changes
  if: needs.detect-changes.outputs.has_changes == 'true'

  permissions:
    contents: read
    id-token: write  # Required for OIDC

  steps:
    - uses: actions/checkout@v4

    - name: Authenticate to Google Cloud (Production)
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: 'projects/987654321/locations/global/workloadIdentityPools/github-pool/providers/github-oidc'
        service_account: 'github-actions-prod@mindmirror-69.iam.gserviceaccount.com'

    # Rest stays the same...
```

### Step 6: Test Production Workflow

```bash
git checkout main
git merge staging
git push origin main

# Monitor workflow in GitHub Actions
```

---

## Phase 3: Cleanup (Remove SA Keys)

**After verifying WIF works in both environments**:

### Remove GitHub Secrets

```bash
# In GitHub repository settings:
# Settings → Secrets and variables → Actions → Repository secrets
# → Delete: GCP_STAGING_SA_KEY
# → Delete: GCP_PRODUCTION_SA_KEY
```

### Delete Service Account Keys (GCP)

```bash
# List keys for staging SA
gcloud iam service-accounts keys list \
  --iam-account="github-actions-staging@mindmirror-staging.iam.gserviceaccount.com"

# Delete each key (except the Google-managed key)
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account="github-actions-staging@mindmirror-staging.iam.gserviceaccount.com"

# Repeat for production SA
gcloud iam service-accounts keys list \
  --iam-account="github-actions-prod@mindmirror-69.iam.gserviceaccount.com"

gcloud iam service-accounts keys delete KEY_ID \
  --iam-account="github-actions-prod@mindmirror-69.iam.gserviceaccount.com"
```

**Verify No Keys Remain**:
```bash
# Should show only 1 key (Google-managed, cannot be deleted)
gcloud iam service-accounts keys list \
  --iam-account="github-actions-staging@mindmirror-staging.iam.gserviceaccount.com" \
  --filter="keyType:USER_MANAGED"
```

---

## Advanced: Fine-Grained Access Control

### Restrict by GitHub Actor (Username)

```bash
# Only allow specific GitHub users to trigger workflows
gcloud iam service-accounts add-iam-policy-binding "${STAGING_SA}" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror" \
  --condition='expression=assertion.actor in ["alice", "bob", "charlie"],title=approved-users-only,description=Only specific users can deploy'
```

### Restrict by Workflow Name

```bash
# Only allow specific workflow to authenticate
gcloud iam service-accounts add-iam-policy-binding "${STAGING_SA}" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror" \
  --condition='expression=assertion.workflow == "Deploy to Staging",title=staging-workflow-only,description=Only staging workflow'
```

### Combine Multiple Conditions

```bash
# Staging branch + approved users + specific workflow
gcloud iam service-accounts add-iam-policy-binding "${STAGING_SA}" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror" \
  --condition='expression=assertion.ref == "refs/heads/staging" && assertion.actor in ["alice", "bob"] && assertion.workflow == "Deploy to Staging",title=staging-constraints,description=Staging branch + approved users + specific workflow'
```

---

## Troubleshooting

### Error: "Failed to generate Google Cloud access token"

**Cause**: Missing `id-token: write` permission

**Fix**:
```yaml
jobs:
  my-job:
    permissions:
      contents: read
      id-token: write  # ← Add this
```

---

### Error: "Permission denied on workload identity pool"

**Cause**: IAM binding not configured correctly

**Fix**:
```bash
# Verify binding exists
gcloud iam service-accounts get-iam-policy "${STAGING_SA}" \
  --project="${STAGING_PROJECT}"

# Look for:
# - role: roles/iam.workloadIdentityUser
# - member: principalSet://iam.googleapis.com/projects/.../attribute.repository/YOUR_REPO
```

---

### Error: "Token validation failed: audience mismatch"

**Cause**: Attribute condition filtering out your repository

**Fix**:
```bash
# Check attribute condition in provider
gcloud iam workload-identity-pools providers describe "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(attributeCondition)"

# Should return: assertion.repository_owner == 'your-org'
# Verify 'your-org' matches your GitHub org exactly
```

---

### Error: "Condition evaluation failed"

**Cause**: IAM condition syntax error or attribute mismatch

**Fix**:
```bash
# Verify condition syntax
gcloud iam service-accounts get-iam-policy "${STAGING_SA}" \
  --project="${STAGING_PROJECT}" \
  --format=json | jq '.bindings[] | select(.role=="roles/iam.workloadIdentityUser") | .condition'

# Common issues:
# - Branch ref should be: "refs/heads/staging" (not just "staging")
# - String comparisons need double quotes: assertion.ref == "refs/heads/main"
# - Array membership: assertion.actor in ["user1", "user2"]
```

---

## Security Best Practices

### 1. Separate Pools Per Environment
```bash
# ✅ Good: Separate pools
staging:   github-pool (in mindmirror-staging project)
production: github-pool (in mindmirror-69 project)

# ❌ Bad: Shared pool across environments
# (Allows staging workflows to potentially access production)
```

### 2. Principle of Least Privilege
```bash
# ✅ Good: Restrict to specific repository and branch
--member="principalSet://.../attribute.repository/your-org/MindMirror"
--condition='assertion.ref == "refs/heads/staging"'

# ❌ Bad: Allow entire pool (any repo in your org)
--member="principalSet://.../workloadIdentityPools/github-pool/*"
```

### 3. Audit Regularly
```bash
# List all WIF bindings for staging SA
gcloud iam service-accounts get-iam-policy \
  github-actions-staging@mindmirror-staging.iam.gserviceaccount.com \
  --project=mindmirror-staging \
  --filter="bindings.role:workloadIdentityUser"
```

### 4. Monitor Usage
```bash
# Cloud Logging filter to see WIF authentications
resource.type="service_account"
protoPayload.methodName="google.iam.credentials.v1.IAMCredentials.GenerateAccessToken"
protoPayload.authenticationInfo.principalEmail="github-actions-staging@mindmirror-staging.iam.gserviceaccount.com"
```

---

## Migration Checklist

**Pre-Migration**:
- [ ] Verify existing workflows use `google-github-actions/auth@v2` (not v0 or v1)
- [ ] Confirm service accounts already exist
- [ ] Backup current workflow files

**Staging Migration**:
- [ ] Create WIF pool in staging project
- [ ] Create GitHub OIDC provider
- [ ] Bind staging SA to pool
- [ ] Update staging workflow
- [ ] Test staging deployment
- [ ] Verify authentication succeeds

**Production Migration**:
- [ ] Create WIF pool in production project
- [ ] Create GitHub OIDC provider
- [ ] Bind production SA to pool
- [ ] Update production workflow
- [ ] Test production deployment
- [ ] Verify authentication succeeds

**Cleanup**:
- [ ] Delete GitHub secret: `GCP_STAGING_SA_KEY`
- [ ] Delete GitHub secret: `GCP_PRODUCTION_SA_KEY`
- [ ] Delete user-managed keys from staging SA
- [ ] Delete user-managed keys from production SA
- [ ] Update documentation
- [ ] Document WIF provider resource names for future reference

---

## Cost Impact

**Workload Identity Federation**: FREE (no additional cost beyond existing SA usage)

**Comparison**:
- Service Account Keys: Free storage, but security risk
- WIF: Free, no storage, no rotation, auto-expiring tokens

**Net Cost**: $0 difference, significant security improvement

---

## References

- [Official WIF Documentation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions OIDC with GCP](https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)
- [Configuring WIF for GitHub](https://github.com/google-github-actions/auth#setup)

---

## Next Steps

1. **Execute Phase 1** (Staging setup)
2. **Test thoroughly** in staging (multiple deploys, different users)
3. **Execute Phase 2** (Production setup)
4. **Execute Phase 3** (Cleanup old keys)
5. **Document provider resource names** for team reference
6. **Update runbooks** with WIF troubleshooting steps

---

**Questions?**

Contact team lead or refer to GCP IAM documentation for advanced WIF scenarios.
