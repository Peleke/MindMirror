# Terrateam + Tofu: Complete Setup Guide
**Goal**: Automate your exact manual workflow with GitOps
**Timeline**: 2-3 hours setup, then fully automated forever

---

## What You're Building

**Before** (Manual):
```bash
act -W .github/workflows/local.yaml  # Build images locally
vim infra/defaults.tfvars            # Update image SHAs manually
cd infra && tofu plan && tofu apply  # Deploy manually
```

**After** (Automated):
```bash
git push origin staging              # → Auto-builds + auto-deploys staging
git push origin main                 # → Auto-builds + creates PR for production
# Review PR → comment "terrateam apply" → deployed
```

---

## Prerequisites

✅ Existing `infra/` Tofu setup (you have this!)
✅ Two GCP projects: staging + production
✅ Two Supabase instances: staging + production
✅ GitHub repository with Actions enabled

---

## Phase 1: Bootstrap (30 minutes)

### Step 1: Install Terrateam GitHub App

1. Go to https://github.com/apps/terrateam
2. Click "Install"
3. Select your repository (`MindMirror`)
4. Grant permissions (read/write to code, pull requests)
5. Complete installation

**Verify**:
```bash
# You should see Terrateam bot added to your repo
# Check: Repository → Settings → GitHub Apps → Installed GitHub Apps
```

### Step 2: Create Staging Branch

```bash
# Create staging branch from main
git checkout main
git pull origin main
git checkout -b staging
git push origin staging

# Protect staging branch (optional but recommended)
# GitHub → Settings → Branches → Add rule for "staging"
```

### Step 3: Setup Workload Identity Federation (WIF)

**Why WIF?** No service account keys = better security. GitHub Actions uses OIDC tokens instead of long-lived keys.

**Staging Setup**:
```bash
export STAGING_PROJECT="mindmirror-staging"  # Or use mindmirror-69 with separate Artifact Registry
export STAGING_PROJECT_NUM=$(gcloud projects describe $STAGING_PROJECT --format='value(projectNumber)')
export GITHUB_REPO="your-org/MindMirror"  # ← Update with your GitHub org/repo

# 1. Create service account
gcloud iam service-accounts create github-actions-staging \
  --project=$STAGING_PROJECT \
  --display-name="GitHub Actions - Staging"

# 2. Grant permissions
for ROLE in roles/run.admin roles/iam.serviceAccountUser roles/artifactregistry.writer; do
  gcloud projects add-iam-policy-binding $STAGING_PROJECT \
    --member="serviceAccount:github-actions-staging@${STAGING_PROJECT}.iam.gserviceaccount.com" \
    --role="$ROLE"
done

# 3. Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 4. Create GitHub OIDC Provider
gcloud iam workload-identity-pools providers create-oidc "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository_owner == '$(echo $GITHUB_REPO | cut -d'/' -f1)'"

# 5. Bind service account to pool (restrict to staging branch)
gcloud iam service-accounts add-iam-policy-binding \
  "github-actions-staging@${STAGING_PROJECT}.iam.gserviceaccount.com" \
  --project="${STAGING_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${STAGING_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GITHUB_REPO}" \
  --condition='expression=assertion.ref == "refs/heads/staging",title=staging-branch-only,description=Only allow staging branch'

# 6. Get Workload Identity Provider resource name (save this!)
gcloud iam workload-identity-pools providers describe "github-oidc" \
  --project="${STAGING_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"

# Example output: projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-oidc
# ↑ You'll need this in the GitHub Actions workflow
```

**Production Setup**:
```bash
export PROD_PROJECT="mindmirror-69"
export PROD_PROJECT_NUM=$(gcloud projects describe $PROD_PROJECT --format='value(projectNumber)')
export GITHUB_REPO="your-org/MindMirror"  # ← Same as above

# 1. Create service account
gcloud iam service-accounts create github-actions-prod \
  --project=$PROD_PROJECT \
  --display-name="GitHub Actions - Production"

# 2. Grant permissions
for ROLE in roles/run.admin roles/iam.serviceAccountUser roles/artifactregistry.writer; do
  gcloud projects add-iam-policy-binding $PROD_PROJECT \
    --member="serviceAccount:github-actions-prod@${PROD_PROJECT}.iam.gserviceaccount.com" \
    --role="$ROLE"
done

# 3. Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROD_PROJECT}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 4. Create GitHub OIDC Provider
gcloud iam workload-identity-pools providers create-oidc "github-oidc" \
  --project="${PROD_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository_owner == '$(echo $GITHUB_REPO | cut -d'/' -f1)'"

# 5. Bind service account to pool (restrict to main branch)
gcloud iam service-accounts add-iam-policy-binding \
  "github-actions-prod@${PROD_PROJECT}.iam.gserviceaccount.com" \
  --project="${PROD_PROJECT}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROD_PROJECT_NUM}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GITHUB_REPO}" \
  --condition='expression=assertion.ref == "refs/heads/main",title=main-branch-only,description=Only allow main branch'

# 6. Get Workload Identity Provider resource name (save this!)
gcloud iam workload-identity-pools providers describe "github-oidc" \
  --project="${PROD_PROJECT}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)"

# Example output: projects/987654321/locations/global/workloadIdentityPools/github-pool/providers/github-oidc
# ↑ You'll need this in the GitHub Actions workflow
```

**✅ No service account keys needed!** WIF uses keyless authentication with OIDC tokens from GitHub (auto-generated, 1-hour expiry).

**Note**: You will still need to add project numbers to GitHub Secrets in Step 4, but these are NOT sensitive credentials - they're public identifiers used to construct WIF resource names.

### Step 4: Configure GitHub Secrets for WIF

The workflows need your GCP project numbers for WIF authentication:

```bash
# Get staging project number
STAGING_PROJECT_NUM=$(gcloud projects describe mindmirror-staging --format='value(projectNumber)')
echo "Staging Project Number: $STAGING_PROJECT_NUM"

# Get production project number
PRODUCTION_PROJECT_NUM=$(gcloud projects describe mindmirror-69 --format='value(projectNumber)')
echo "Production Project Number: $PRODUCTION_PROJECT_NUM"
```

**Add to GitHub Secrets**:
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add these secrets:
   - Name: `GCP_STAGING_PROJECT_NUM`
     Value: (paste your staging project number)
   - Name: `GCP_PRODUCTION_PROJECT_NUM`
     Value: (paste your production project number)

**Note**: These are project numbers (numeric IDs), NOT project IDs (string names). They're used to construct the WIF provider resource names in the workflows.

### Step 5: Setup Artifact Registry (if not exists)

**Staging**:
```bash
gcloud artifacts repositories create mindmirror \
  --repository-format=docker \
  --location=us-east4 \
  --project=$STAGING_PROJECT \
  --description="MindMirror staging container images"
```

**Production** (already exists at `mindmirror-69`):
```bash
# Verify it exists
gcloud artifacts repositories list --project=mindmirror-69
```

### Step 6: Update `generate-tfvars.sh` with Your Staging Project

Edit `scripts/generate-tfvars.sh`:
```bash
case "$ENVIRONMENT" in
    staging)
        PROJECT_ID="mindmirror-staging"  # ← Update this
        PROJECT_NUM_ID="YOUR_STAGING_PROJECT_NUMBER"  # ← Update this (from Step 4)
        # ... rest stays the same
```

Get your staging project number:
```bash
gcloud projects describe mindmirror-staging --format='value(projectNumber)'
# → Update PROJECT_NUM_ID in generate-tfvars.sh
```

---

## Phase 2: Deploy Infrastructure Files (10 minutes)

All files already created! ✅ Just commit them:

```bash
git checkout main
git pull origin main

# Verify files exist
ls -la .terrateam/config.yml
ls -la .github/workflows/staging-deploy.yml
ls -la .github/workflows/production-deploy.yml
ls -la scripts/generate-tfvars.sh
ls -la VERSION

# Commit everything
git add .terrateam/ .github/workflows/ scripts/ VERSION docs/
git commit -m "feat: add Terrateam automation for staging + production"
git push origin main

# Merge to staging
git checkout staging
git merge main
git push origin staging
```

---

## Phase 3: First Deployment (30 minutes)

### Test Staging Deploy

**Trigger**: Push to `staging` branch

```bash
# Make a trivial change to trigger deploy
git checkout staging
echo "# Test staging deploy" >> README.md
git add README.md
git commit -m "test: trigger staging deploy"
git push origin staging
```

**Watch the magic**:
1. Go to GitHub → Actions → "Deploy to Staging"
2. Watch workflow build images → push to staging registry
3. Workflow commits `staging.auto.tfvars` back to branch
4. Terrateam detects tfvars change → auto-plans → auto-applies
5. Check Terrateam comment on commit (plan + apply status)

**Verify Deployment**:
```bash
# Check Cloud Run services in staging
gcloud run services list --project=mindmirror-staging --region=us-east4

# Test staging API
STAGING_AGENT_URL=$(gcloud run services describe agent-service \
  --project=mindmirror-staging \
  --region=us-east4 \
  --format='value(status.url)')

curl $STAGING_AGENT_URL/health
```

### Test Production Deploy

**Trigger**: Push to `main` branch

```bash
# Merge staging to main (or make change on main)
git checkout main
git merge staging --no-ff -m "feat: automated deployment system"
git push origin main
```

**Watch the workflow**:
1. GitHub Actions → "Deploy to Production"
2. Workflow builds images → pushes to production registry
3. Workflow creates PR with `production.auto.tfvars` update
4. Go to Pull Requests tab → Review the PR

**Review Terrateam Plan**:
1. Wait 1-2 minutes for Terrateam comment on PR
2. Review the plan carefully:
   - Check image tags are correct
   - Verify only expected services are changing
   - No unexpected resource deletions/replacements

**Approve Deployment**:
```
# In PR, comment:
terrateam apply
```

**Watch Terrateam apply**:
- Terrateam will apply changes to production
- Check logs in Terrateam comment
- Verify success

**Merge PR**:
```bash
# After successful deployment, merge the PR
gh pr merge --squash
```

**Verify Production**:
```bash
gcloud run services list --project=mindmirror-69 --region=us-east4

PROD_AGENT_URL=$(gcloud run services describe agent-service \
  --project=mindmirror-69 \
  --region=us-east4 \
  --format='value(status.url)')

curl $PROD_AGENT_URL/health
```

---

## Phase 4: Daily Workflow (Forever)

### Deploying to Staging

```bash
# 1. Work on feature branch
git checkout -b feature/new-thing

# 2. Make changes
# ... code code code

# 3. Merge to staging
git checkout staging
git merge feature/new-thing
git push origin staging

# → Auto-deploys in 3-5 minutes (no approval needed)
```

### Deploying to Production

```bash
# 1. Merge staging to main (or cherry-pick specific commits)
git checkout main
git merge staging --no-ff
git push origin main

# 2. Review PR created by GitHub Actions
# → Go to Pull Requests tab

# 3. Wait for Terrateam plan (1-2 minutes)

# 4. Review plan carefully

# 5. Approve: comment "terrateam apply"

# 6. Wait for deployment (2-3 minutes)

# 7. Merge PR
gh pr merge --squash
```

### Updating Version

```bash
# When ready for new semantic version
echo "1.1.0" > VERSION
git add VERSION
git commit -m "chore: bump version to 1.1.0"
git push origin staging  # Or main

# Next deploy will use v1.1.0-<sha> tags
```

---

## Troubleshooting

### Terrateam Not Commenting on PR

**Check**:
1. Terrateam GitHub App installed? (Settings → GitHub Apps)
2. `.terrateam/config.yml` exists and valid?
3. `infra/*.auto.tfvars` file changed in PR?

**Fix**:
```bash
# Manually trigger Terrateam
# Comment on PR: terrateam plan
```

### GitHub Actions Failing to Push Images

**Check**:
1. Workload Identity Federation configured correctly?
2. Service account has `roles/artifactregistry.writer`?
3. Artifact Registry exists in target project?
4. Workflow has `permissions.id-token: write`?

**Verify WIF Setup**:
```bash
# Check workload identity pool exists
gcloud iam workload-identity-pools describe github-pool \
  --project=PROJECT_ID \
  --location=global

# Verify service account binding
gcloud iam service-accounts get-iam-policy \
  github-actions-staging@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID
```

**Fix**:
```bash
# Re-grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-actions-staging@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

### Tofu Plan Fails

**Check**:
1. Secrets exist in target GCP project?
2. `project_id` in auto.tfvars correct?
3. Service account has Cloud Run permissions?

**Fix**:
```bash
# List secrets
gcloud secrets list --project=PROJECT_ID

# Grant Cloud Run admin
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

### Services Deploy But Don't Start

**Check**:
1. Image exists in Artifact Registry?
2. Secrets accessible from Cloud Run service?
3. Service account has Secret Manager access?

**Fix**:
```bash
# Check service logs
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service" \
  --project=PROJECT_ID
```

### Workload Identity Federation Authentication Errors

**Error**: "Failed to generate Google Cloud access token" or "OIDC token verification failed"

**Check**:
1. Workflow has `permissions.id-token: write` at job level
2. Repository matches attribute condition in WIF provider
3. Branch matches IAM binding condition
4. Workload Identity Provider resource name is correct

**Verify WIF Configuration**:
```bash
# Get provider resource name (should match workflow)
gcloud iam workload-identity-pools providers describe github-oidc \
  --project=PROJECT_ID \
  --location=global \
  --workload-identity-pool=github-pool \
  --format="value(name)"

# Check attribute mapping and conditions
gcloud iam workload-identity-pools providers describe github-oidc \
  --project=PROJECT_ID \
  --location=global \
  --workload-identity-pool=github-pool \
  --format=yaml
```

**Common Fixes**:

1. **Missing `id-token` permission**:
```yaml
# Add to workflow job
permissions:
  contents: read
  id-token: write  # Required for OIDC
```

2. **Wrong repository in attribute condition**:
```bash
# Update provider attribute condition
gcloud iam workload-identity-pools providers update-oidc github-oidc \
  --project=PROJECT_ID \
  --location=global \
  --workload-identity-pool=github-pool \
  --attribute-condition="assertion.repository_owner == 'your-org'"
```

3. **Branch condition mismatch**:
```bash
# Check current binding conditions
gcloud iam service-accounts get-iam-policy \
  github-actions-staging@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID \
  --format=yaml

# Re-bind with correct branch condition
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-staging@PROJECT_ID.iam.gserviceaccount.com \
  --project=PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUM/locations/global/workloadIdentityPools/github-pool/attribute.repository/your-org/MindMirror" \
  --condition='expression=assertion.ref == "refs/heads/staging",title=staging-branch-only'
```

---

## Advanced: Cloud Run v2 Migration (Future)

**Current**: `google_cloud_run_service` (legacy v1)
**Target**: `google_cloud_run_v2_service`

**When**: After automation is stable (December-January)

**Steps**:
1. Create feature branch: `feature/cloud-run-v2`
2. Update one service module to use v2 resource
3. Test in staging
4. Gradually migrate all services
5. Add VPC networking, secret volumes, IAM restrictions

See `docs/devops-strategy.md` for detailed migration plan.

---

## Cost Estimates

| Resource | Staging | Production | Notes |
|----------|---------|------------|-------|
| Cloud Run | ~$20/month | ~$50/month | 8 services, min instances |
| Artifact Registry | ~$5/month | ~$10/month | Image storage |
| Cloud Logging | Free tier | Free tier | <50GB/month |
| Supabase | $25/month | $25/month | Pro tier each |
| Qdrant Cloud | $25/month | $95/month | Different cluster sizes |
| **Total** | **~$75/month** | **~$180/month** | Scalable as needed |

---

## Security Checklist

- [ ] Service accounts use least privilege (roles/run.admin, not roles/owner)
- [ ] Workload Identity Federation configured (no service account keys!)
- [ ] WIF pools restrict access by repository and branch
- [ ] Workflows have `permissions.id-token: write` enabled
- [ ] Separate Supabase instances (no production data in staging)
- [ ] Separate GCP Secret Manager per project
- [ ] Terrateam auto-apply disabled for production
- [ ] Branch protection enabled (require PR reviews)
- [ ] Manual approval required for production (terrateam apply comment)

---

## What You've Automated

✅ **Docker builds**: Auto-build on push
✅ **Image tagging**: Semantic versioning + git SHA
✅ **Image pushing**: To environment-specific registries
✅ **Tofu variables**: Auto-generated tfvars files
✅ **Staging deploys**: Fully automated (no approval)
✅ **Production deploys**: PR-driven with manual approval
✅ **GitOps**: All infrastructure changes in git
✅ **Rollback**: Revert PR or push previous version tag

---

## What You Still Do Manually

⏸️ **Gateway updates**: Run `scripts/update-gateway.sh` when GraphQL schemas change (automate in Phase 2)
⏸️ **Database migrations**: Run manually via Cloud Run Job (automate in Phase 2)
⏸️ **Version bumps**: Edit `VERSION` file manually (or use conventional commits later)

---

## Success Criteria

**Week 1** (Now):
- [ ] Terrateam installed
- [ ] Staging deploys automatically
- [ ] Production deploys via PR + approval
- [ ] No manual `tofu apply` needed

**Week 2**:
- [ ] First production deploy via automation successful
- [ ] Team comfortable with PR-driven deployment
- [ ] `defaults.tfvars` deprecated (use auto.tfvars only)

**Week 4**:
- [ ] 10+ automated deploys to staging
- [ ] 3+ automated deploys to production
- [ ] Zero manual tofu commands run

---

## Next Steps

1. **Complete Phase 1-3** (bootstrap, deploy files, first deployment)
2. **Use for 2-4 weeks** (build confidence)
3. **Phase 2 enhancements** (December):
   - Automate gateway composition
   - Automate database migrations
   - Migrate to Cloud Run v2
4. **Phase 3 hardening** (January):
   - Add VPC networking
   - Backend service IAM restrictions
   - Custom monitoring dashboards

---

## Support

**Documentation**:
- `docs/devops-terrateam-strategy.md` - Full architecture
- `docs/STAGING-VS-PRODUCTION.md` - Environment separation details
- `docs/devops-strategy.md` - Original DevOps plan

**Runbooks**:
- Manual gateway update: `scripts/update-gateway.sh all`
- Health check all services: `scripts/health-check-all.sh production`
- Generate tfvars manually: `scripts/generate-tfvars.sh staging v1.0.0-abc123`

**Help**:
- Terrateam docs: https://docs.terrateam.io
- OpenTofu docs: https://opentofu.org/docs
- GitHub Actions: https://docs.github.com/actions

---

**You're ready to ship! 🚀**
