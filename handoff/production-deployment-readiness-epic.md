# Production Deployment Readiness Epic

**Date:** 2025-10-31
**Status:** Ready to implement
**Context:** Staging workflows complete ✅ | Production needs 2 gateway workflows + approval gates

---

## Quick Summary

**Working:** Staging 4-phase deployment (build → deploy services → build gateway → deploy gateway)
**Missing:** Production gateway workflows (phases 3-4)
**Decisions Made:**
- Service naming: Bare names (no `-production` suffix)
- Approval: Option 3 (PR review + GitHub Environment gates)
- Gateway triggers: Unconditional (optimize later)

---

## Critical Tasks

### 1. Create `gateway-deploy-production.yml`
Copy from `gateway-deploy.yml`, update:
- Trigger: `Tofu Apply - Production` on `main` branch
- Project: `mindmirror-prod`
- Service names: Remove `-staging` suffix → `gateway`
- WIF: `GCP_PRODUCTION_PROJECT_NUM`
- SA: `github-actions-production@mindmirror-prod`
- tfvars: `production.auto.tfvars`
- **Key:** Create PR (don't commit directly)

### 2. Create `tofu-apply-gateway-production.yml`
Copy from `tofu-apply-gateway-staging.yml`, update:
- Same changes as above, PLUS:
- Add approval gate:
  ```yaml
  environment:
    name: production
    url: https://console.cloud.google.com/run?project=mindmirror-prod
  ```
- Backend: `-backend-config=production.backend.hcl`

### 3. Configure GitHub Environment
- Settings → Environments → `production`
- Add required reviewers
- Restrict to `main` branch only

### 4. Verify Service Naming
Check `infra/variables.tf` and `defaults.tfvars`:
- Confirm: `agent_service_name = "agent-service"` (no suffix)
- Ensure all workflows match

---

## Environment Variables

| Variable | Staging | Production |
|----------|---------|------------|
| Project | `mindmirror-69` | `mindmirror-prod` |
| WIF Secret | `GCP_STAGING_PROJECT_NUM` | `GCP_PRODUCTION_PROJECT_NUM` |
| SA | `github-actions-staging@...` | `github-actions-production@...` |
| Service suffix | `-staging` | none |
| Backend | `staging.backend.hcl` | `production.backend.hcl` |

---

## Pre-Flight Checks

Before first production deploy:
- [ ] Both gateway workflows created
- [ ] GitHub Environment configured with approvers
- [ ] GCP resources validated (run validation commands below)
- [ ] Service naming verified
- [ ] Scripts support `production` parameter

**GCP Validation:**
```bash
gcloud config set project mindmirror-prod
gcloud projects describe mindmirror-prod
gcloud iam workload-identity-pools list --location=global --project=mindmirror-prod
gcloud iam service-accounts list --project=mindmirror-prod --filter="email:github-actions"
gcloud artifacts repositories describe mindmirror --location=us-east4 --project=mindmirror-prod
gcloud secrets list --project=mindmirror-prod --filter="name:service-urls"
```

---

## Approval Flow

**Services (Phase 1-2):**
1. Push to `main` → `production-deploy.yml` creates PR
2. Manual PR review
3. Merge PR
4. **GitHub Environment approval** in UI
5. Services deploy

**Gateway (Phase 3-4):**
6. Gateway build triggered → creates PR
7. Manual PR review
8. Merge PR
9. **GitHub Environment approval** in UI
10. Gateway deploys

---

## Rollback

If deployment fails:
```bash
# Rollback services
cd infra
git checkout HEAD~1 -- production.auto.tfvars
git commit -m "rollback: revert deployment"
git push origin main
# Approve rollback

# Or manual intervention
gcloud run deploy SERVICE_NAME \
  --image=KNOWN_GOOD_TAG \
  --region=us-east4 \
  --project=mindmirror-prod
```

---

## Next Actions

1. Create both gateway workflows
2. Test with manual trigger on staging first
3. Configure GitHub Environment
4. Validate GCP resources
5. Do test deployment to production

**Total time:** ~2-3 hours

---

**Resume Point:** Start with Task 1 (create gateway-deploy-production.yml)
