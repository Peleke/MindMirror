# Production Gateway Deployment - Quick Start

**TL;DR:** Two-phase pipeline test: Feature→Staging (test existing), Staging→Main (test new production workflows)

---

## ⚡ Quick Commands

### Phase 1: Feature Branch → Staging (Test Staging Workflows)

```bash
# 1. Create feature branch
git checkout staging
git checkout -b feature/add-production-gateway-workflows

# 2. Add files
git add .github/workflows/gateway-deploy-production.yml
git add .github/workflows/tofu-apply-gateway-production.yml
git add handoff/

# 3. Commit
git commit -m "feat(workflows): add production gateway deployment workflows"

# 4. Push
git push origin feature/add-production-gateway-workflows

# 5. Create PR
gh pr create --base staging --head feature/add-production-gateway-workflows \
  --title "feat: Add production gateway deployment workflows" \
  --body "Adds production gateway workflows with approval gates"

# 6. Merge PR (after review)
gh pr merge --squash --delete-branch

# 7. WATCH: https://github.com/{org}/MindMirror/actions
# Expected: 4 staging workflows run (all green)
```

---

### Phase 2: Staging → Main (Test Production Workflows)

**⚠️ BEFORE STARTING: Configure GitHub Environment!**

```bash
# Go to: GitHub repo → Settings → Environments → New environment
# Name: "production"
# Add required reviewers
# Deployment branches: "main" only
```

**Then proceed:**

```bash
# 1. Create PR from staging to main
git checkout staging
git pull origin staging

gh pr create --base main --head staging \
  --title "feat: Production gateway deployment workflows" \
  --body "Adds production gateway workflows with approval gates. Requires GitHub Environment 'production' configured."

# 2. Review and merge PR
gh pr merge --squash

# 3. Pull main
git checkout main
git pull origin main

# 4. WATCH: https://github.com/{org}/MindMirror/actions
# Expected cascade:
#   1. Deploy to Production (creates PR)
#   2. Review + merge PR
#   3. Tofu Apply - Production ⏸️ APPROVE IN UI
#   4. Deploy Gateway to Production (creates PR)
#   5. Review + merge PR
#   6. Tofu Apply - Gateway (Production) ⏸️ APPROVE IN UI
```

---

## ✅ Quick Verification

### After Staging Deploy
```bash
# Check staging gateway health
curl https://gateway-staging-{hash}.run.app/healthcheck | jq '.'
```

### After Production Deploy
```bash
# Get production gateway URL
gcloud run services describe gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="value(status.url)"

# Health check
curl $(gcloud run services describe gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="value(status.url)")/healthcheck | jq '.'
```

---

## 🚨 If Something Breaks

### Workflow Fails
```bash
# Check logs in GitHub Actions
# Common fixes:
# - Missing GitHub Environment → Create it in Settings
# - Missing secret → Add GCP_PRODUCTION_PROJECT_NUM
# - Re-run failed workflow manually
```

### Gateway Health Fails
```bash
# Gateway just deployed, needs time to start
# Wait 30s, then check:
curl {GATEWAY_URL}/healthcheck

# If still failing, check Cloud Run logs:
gcloud run services logs read gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --limit=50
```

### Need to Rollback
```bash
# Revert production.auto.tfvars to previous version
cd infra
git checkout HEAD~1 -- production.auto.tfvars
git commit -m "rollback: production deployment"
git push origin main
# Then approve in GitHub Actions
```

---

## 📋 Pre-Flight Checklist

Before starting Phase 2 (production):

- [ ] GitHub Environment "production" configured
- [ ] Required reviewers added to environment
- [ ] `GCP_PRODUCTION_PROJECT_NUM` secret exists
- [ ] GCP production project verified (`gcloud projects describe mindmirror-prod`)
- [ ] Phase 1 (staging) completed successfully

---

## 🎯 Success Looks Like

**Staging (Phase 1):**
- ✅ 4 workflows complete: Deploy → Tofu Apply → Gateway Deploy → Gateway Apply
- ✅ All green checkmarks
- ✅ Gateway health check passes

**Production (Phase 2):**
- ✅ 2 approval prompts (you click "Approve" in GitHub UI)
- ✅ 2 GitHub issues created (success notifications)
- ✅ Gateway health check passes
- ✅ All services running in GCP Cloud Run console

---

**Time Required:**
- Phase 1: ~15-20 min
- Phase 2: ~25-30 min
- **Total: ~45-50 min**

**Full details:** See `production-gateway-deployment-walkthrough.md`
