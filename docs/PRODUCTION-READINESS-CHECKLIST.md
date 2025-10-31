# Production Deployment Readiness Checklist 🚀

**Status:** Ready for staging test → Production deployment after Vercel cutover

**Timeline:**
- Tomorrow: Test staging end-to-end
- After Vercel cutover to `...-staging`: Production deployment

---

## Critical Issues to Fix BEFORE Production 🔴

### 1. Missing Terraform Outputs (BLOCKING)

**Problem:** `infra/outputs.tf` is missing 4 service URL outputs needed by gateway rebuild scripts

**Missing Outputs:**
```terraform
# Add to infra/outputs.tf:

output "meals_service_url" {
  description = "Meals service URL"
  value       = module.meals_service.service_url
}

output "movements_service_url" {
  description = "Movements service URL"
  value       = module.movements_service.service_url
}

output "practices_service_url" {
  description = "Practices service URL"
  value       = module.practices_service.service_url
}

output "users_service_url" {
  description = "Users service URL"
  value       = module.users_service.service_url
}
```

**Why Critical:**
- `scripts/extract-service-urls.sh` expects these 7 service URLs
- Gateway build will fail without all service URLs
- Will cause `tofu-apply-staging.yml` extract job to fail

**Fix Location:** `infra/outputs.tf` (line 30, after `habits_service_url`)

**Testing:**
```bash
cd infra
tofu output -json | jq '.meals_service_url, .movements_service_url, .practices_service_url, .users_service_url'
# Should show 4 URLs, not "null"
```

---

### 2. Production Workflows Need Gateway Two-Phase Pattern

**Problem:** `production-deploy.yml` still includes gateway in build matrix (will break like staging did)

**Required Changes:**

#### A. Update `production-deploy.yml` ✅ Required
```yaml
# Line 68-73: Add mesh_gateway to exclude list
exclude:
  - service: web_app
  - service: mobile_app
  - service: celery_worker
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Gateway excluded (two-phase deployment pattern)
  # Gateway rebuilt after services deploy with service URLs
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - service: mesh_gateway
```

#### B. Create `gateway-deploy-production.yml` ✅ Required
**Location:** `.github/workflows/gateway-deploy-production.yml`

**Differences from Staging:**
- Uses `mindmirror-prod` project
- Uses `service-urls-production` secret
- Manual trigger only (no auto-trigger from workflow_run)
- Stricter validation and testing

**Template:**
```yaml
name: Deploy Gateway to Production

on:
  workflow_dispatch:  # Manual trigger ONLY
    inputs:
      version_tag:
        description: 'Version tag (e.g., v1.0.0-abc1234)'
        required: true
        type: string

env:
  GCP_PROJECT_ID: mindmirror-prod
  GCP_REGION: us-east4
  ARTIFACT_REGISTRY: us-east4-docker.pkg.dev
  ARTIFACT_REPO: mindmirror

jobs:
  build-gateway:
    # Same as staging but with production config
    # ...
```

#### C. Create `tofu-apply-gateway-production.yml` ✅ Required
**Location:** `.github/workflows/tofu-apply-gateway-production.yml`

**Differences from Staging:**
- Manual approval gate via GitHub Environment
- More comprehensive health checks
- Rollback plan in case of failure
- No auto-approval

**Environment Protection:**
```yaml
jobs:
  apply-gateway:
    environment:
      name: production
      url: https://gateway.mindmirror.app
    # This triggers manual approval in GitHub
```

#### D. Update `tofu-apply-production.yml` ✅ Required
**Add extract-service-urls job** (same pattern as staging)

```yaml
# Add after existing apply job:
extract-service-urls:
  needs: apply
  runs-on: ubuntu-latest
  if: ${{ needs.apply.result == 'success' }}
  permissions:
    contents: read
    id-token: write
  steps:
    - Extract service URLs from Terraform outputs
    - Save to projects/mindmirror-prod/secrets/service-urls-production
    - Notify that gateway can now be manually deployed
```

---

## GCP Configuration Checklist ✅

### Staging (mindmirror-69)

#### Secret Manager
- [ ] Secret exists: `service-urls-staging`
- [ ] IAM permissions for `github-actions-staging@mindmirror-69.iam.gserviceaccount.com`:
  - `roles/secretmanager.admin` (create/update secrets)
  - `roles/secretmanager.secretAccessor` (read secrets)

**Verify:**
```bash
gcloud secrets describe service-urls-staging --project=mindmirror-69

gcloud secrets get-iam-policy service-urls-staging --project=mindmirror-69
# Should show github-actions-staging with secretmanager permissions
```

#### Service Account Permissions
```bash
# Check github-actions-staging permissions
gcloud projects get-iam-policy mindmirror-69 \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-staging@mindmirror-69.iam.gserviceaccount.com"

# Required roles:
# - roles/run.admin (deploy Cloud Run)
# - roles/iam.serviceAccountUser (act as service accounts)
# - roles/secretmanager.admin (manage secrets)
# - roles/secretmanager.secretAccessor (read secrets)
# - roles/artifactregistry.writer (push images)
```

### Production (mindmirror-prod)

#### Secret Manager Setup
- [ ] Create secret: `service-urls-production`
- [ ] Configure IAM for `github-actions-production@mindmirror-prod.iam.gserviceaccount.com`

**Commands:**
```bash
# Create production secret (initially empty)
gcloud secrets create service-urls-production \
  --project=mindmirror-prod \
  --replication-policy="automatic"

# Grant permissions
gcloud secrets add-iam-policy-binding service-urls-production \
  --project=mindmirror-prod \
  --member="serviceAccount:github-actions-production@mindmirror-prod.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"

gcloud secrets add-iam-policy-binding service-urls-production \
  --project=mindmirror-prod \
  --member="serviceAccount:github-actions-production@mindmirror-prod.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### Service Account Permissions
```bash
# Same roles as staging, verify exists:
gcloud projects get-iam-policy mindmirror-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-production@mindmirror-prod.iam.gserviceaccount.com"
```

---

## GitHub Configuration Checklist ✅

### Secrets

**Staging:**
- [x] `GCP_STAGING_PROJECT_NUM` - Project numerical ID (3858903851)

**Production:**
- [x] `GCP_PRODUCTION_PROJECT_NUM` - Project numerical ID (435339726777)

**Verify:**
```bash
gh secret list
# Should show both secrets
```

### Environment Protection Rules

**Create Production Environment:**
```bash
# Via GitHub UI (required for manual approval):
# Settings → Environments → New environment → "production"
# Add reviewers: [your team members]
# Set deployment branches: main only
```

**Result:** `tofu-apply-gateway-production.yml` will require approval before deploying

---

## Scripts Validation ✅

All 4 scripts exist and are executable:
- [x] `scripts/extract-service-urls.sh`
- [x] `scripts/save-urls-to-secrets.sh`
- [x] `scripts/build-gateway-with-urls.sh`
- [x] `scripts/generate-tfvars.sh` (with --gateway-only)

**Pre-Production Testing:**
```bash
# Test on staging first to validate scripts work
cd infra
tofu init -backend-config=staging.backend.hcl
tofu output -json > /tmp/staging-outputs.json

# Test extract script
../scripts/extract-service-urls.sh staging . > /tmp/service-urls.json
cat /tmp/service-urls.json | jq '.'

# Verify all 7 URLs are present
jq 'keys' /tmp/service-urls.json
# Should show: ["agent_service_url", "habits_service_url", "journal_service_url",
#               "meals_service_url", "movements_service_url", "practices_service_url",
#               "users_service_url"]
```

---

## Deployment Flow Documentation

### Staging Flow (Automated)
```
Push to staging
  └─> staging-deploy.yml (services only)
      └─> tofu-apply-staging.yml (deploy + extract URLs)
          └─> gateway-deploy.yml (build gateway with URLs) [AUTO-TRIGGERED]
              └─> tofu-apply-gateway-staging.yml (deploy gateway) [AUTO-TRIGGERED]
                  └─> SUCCESS! Gateway live with correct URLs
```

### Production Flow (Controlled)
```
Merge to main
  └─> production-deploy.yml (services only, creates PR)
      └─> REVIEW PR & Terrateam plan
          └─> Comment "terrateam apply"
              └─> tofu-apply-production.yml (deploy + extract URLs)
                  └─> MANUAL: Trigger gateway-deploy-production.yml
                      └─> REVIEW: Gateway build completion
                          └─> MANUAL: Trigger tofu-apply-gateway-production.yml
                              └─> APPROVAL GATE: Review deployment plan
                                  └─> APPROVED: Gateway deploys to production
                                      └─> SUCCESS! Production gateway live
```

**Key Differences:**
| Aspect | Staging | Production |
|--------|---------|------------|
| Services Deploy | Auto on push | PR + Manual approval |
| URL Extraction | Auto after Tofu apply | Auto after Tofu apply |
| Gateway Build | Auto-triggered | Manual trigger only |
| Gateway Deploy | Auto-approved | Approval gate required |
| Testing | Automated health check | Manual validation required |

---

## Pre-Production Testing Plan 📋

### Phase 1: Fix & Validate (Tomorrow)
1. ✅ Add 4 missing outputs to `infra/outputs.tf`
2. ✅ Commit and push to `workflow` branch
3. ✅ Test staging deployment end-to-end:
   ```bash
   # Push small change to trigger workflow
   echo "# Gateway test" >> README.md
   git add README.md
   git commit -m "test: staging gateway workflow"
   git push origin workflow:staging

   # Watch workflows cascade
   gh run watch
   ```
4. ✅ Verify:
   - All services deploy successfully
   - Service URLs extracted and saved to Secret Manager
   - Gateway builds with correct URLs
   - Gateway deploys and passes health check
   - Gateway `/graphql` endpoint works
   - Can query federated schema

### Phase 2: Production Workflow Creation
1. ✅ Create `gateway-deploy-production.yml`
2. ✅ Create `tofu-apply-gateway-production.yml`
3. ✅ Update `production-deploy.yml` (exclude gateway)
4. ✅ Update `tofu-apply-production.yml` (add URL extraction)
5. ✅ Create GitHub "production" environment with reviewers
6. ✅ Test manually with workflow_dispatch

### Phase 3: Vercel Cutover & Production Deploy
1. ✅ Vercel DNS update to `...-staging`
2. ✅ Verify staging working perfectly via new domain
3. ✅ Merge `workflow` branch to `main`
4. ✅ Trigger production deployment
5. ✅ Monitor services deployment
6. ✅ Manually trigger gateway build (review first)
7. ✅ Approve gateway deployment (review plan carefully)
8. ✅ Validate production gateway health
9. ✅ Run integration tests
10. ✅ Monitor for 30 minutes, rollback if issues

---

## Rollback Strategy 🔄

### If Services Fail in Production
```bash
# Revert to previous working image tags
# Update infra/production.auto.tfvars with old tags
# Terrateam will apply old configuration
git revert <bad-commit>
git push origin main
# Comment "terrateam apply" on revert PR
```

### If Gateway Fails in Production
**Advantage:** Gateway failure doesn't affect services!

```bash
# Option 1: Redeploy previous gateway version
gh workflow run gateway-deploy-production.yml \
  -f version_tag=v1.0.0-previous-working-sha

# Option 2: Manual Cloud Run rollback
gcloud run services update-traffic gateway \
  --to-revisions=gateway-xxx-previous=100 \
  --region=us-east4 \
  --project=mindmirror-prod

# Option 3: Revert gateway tfvars
git revert <gateway-commit>
# Trigger gateway deployment with old image
```

---

## Success Criteria for Production 🎯

### Services Deployment
- [ ] All 7 services deploy successfully to Cloud Run
- [ ] Health checks pass for all services
- [ ] Service URLs extracted and saved to production Secret Manager
- [ ] No Terraform errors or warnings
- [ ] All services accessible via their Cloud Run URLs

### Gateway Deployment
- [ ] Gateway builds with all 7 service URLs from Secret Manager
- [ ] Gateway image pushed to production Artifact Registry
- [ ] Gateway deploys to Cloud Run successfully
- [ ] Gateway health check passes (3/3 retries)
- [ ] Gateway `/graphql` endpoint accessible
- [ ] Can query federated schema (test query succeeds)
- [ ] All 7 subgraph schemas federated correctly

### Integration Tests
- [ ] Web app can query production gateway
- [ ] Mobile app can query production gateway (after app update)
- [ ] JWT authentication works through gateway
- [ ] Cross-service queries work (e.g., journal + agent + habits)
- [ ] No CORS errors
- [ ] Response times acceptable (<2s for complex queries)

### Monitoring
- [ ] Cloud Run logs showing no errors
- [ ] Gateway logs showing successful subgraph connections
- [ ] No 5xx errors in gateway
- [ ] All services reporting healthy in Cloud Run console

---

## Emergency Contacts & Resources 📞

### During Deployment
- **GitHub Actions:** https://github.com/anthropics/mindmirror/actions
- **Staging Gateway:** https://gateway-staging-xxx.run.app/graphql
- **Production Gateway:** https://gateway-xxx.run.app/graphql
- **Terrateam:** Check PR comments for plan/apply status

### GCP Consoles
- **Staging:** https://console.cloud.google.com/run?project=mindmirror-69
- **Production:** https://console.cloud.google.com/run?project=mindmirror-prod
- **Secret Manager:** https://console.cloud.google.com/security/secret-manager

### Logs
```bash
# View gateway logs (staging)
gcloud run services logs read gateway-staging \
  --project=mindmirror-69 \
  --region=us-east4 \
  --limit=50

# View gateway logs (production)
gcloud run services logs read gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --limit=50
```

---

## Production Deployment Runbook 📖

### Day Before Deployment
1. ✅ Fix missing Terraform outputs
2. ✅ Test staging end-to-end
3. ✅ Create production workflows
4. ✅ Set up GitHub production environment
5. ✅ Create production Secret Manager secret
6. ✅ Review all changes with team
7. ✅ Schedule deployment time (low traffic period)
8. ✅ Notify team of deployment

### Deployment Day

**Pre-Deployment (15 min):**
```bash
# 1. Final staging verification
curl -f https://gateway-staging-xxx.run.app/healthcheck | jq '.'

# 2. Verify production Secret Manager ready
gcloud secrets describe service-urls-production --project=mindmirror-prod

# 3. Check GitHub Actions status
gh run list --workflow=production-deploy.yml --limit=1

# 4. Verify no active incidents
# Check monitoring dashboards
```

**Services Deployment (20-30 min):**
```bash
# 1. Merge workflow branch to main
git checkout main
git merge workflow
git push origin main

# 2. Monitor production-deploy.yml
gh run watch

# 3. Review PR created by workflow
gh pr list --label=production

# 4. Review Terrateam plan (2-3 min wait)
# Check PR comments for plan output

# 5. Approve services deployment
# Comment on PR: "terrateam apply"

# 6. Monitor tofu-apply-production.yml
gh run watch

# 7. Verify services deployed
gcloud run services list --project=mindmirror-prod --region=us-east4

# 8. Check service URLs saved to Secret Manager
gcloud secrets versions access latest \
  --secret=service-urls-production \
  --project=mindmirror-prod | jq '.'
```

**Gateway Deployment (15-20 min):**
```bash
# 1. Manually trigger gateway build
gh workflow run gateway-deploy-production.yml \
  -f version_tag=v1.0.0-abc1234  # Use actual version from services deployment

# 2. Monitor gateway-deploy-production.yml
gh run watch

# 3. Verify gateway image pushed
gcloud artifacts docker images list \
  us-east4-docker.pkg.dev/mindmirror-prod/mindmirror/mesh \
  --limit=1

# 4. Manually trigger gateway deployment
gh workflow run tofu-apply-gateway-production.yml

# 5. APPROVAL GATE: Review deployment plan
# GitHub will pause for approval
# Review plan carefully, then approve in GitHub UI

# 6. Monitor gateway deployment
gh run watch

# 7. Verify gateway health
GATEWAY_URL=$(gcloud run services describe gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="value(status.url)")

curl -f "${GATEWAY_URL}/healthcheck" | jq '.'

# 8. Test GraphQL endpoint
curl -X POST "${GATEWAY_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { types { name } } }"}'
```

**Post-Deployment Validation (30 min):**
```bash
# 1. Run integration tests
# [Your test suite commands]

# 2. Monitor logs for errors
gcloud run services logs read gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --limit=50 \
  --format="table(time,severity,textPayload)"

# 3. Check all services responding
for service in agent journal habits meals movements practices users; do
  echo "Testing ${service}..."
  gcloud run services describe ${service}-service \
    --project=mindmirror-prod \
    --region=us-east4 \
    --format="value(status.url)"
done

# 4. Monitor for 30 minutes
# Watch dashboards, logs, error rates
# Be ready to rollback if issues detected
```

---

## Known Issues & Workarounds ⚠️

### Issue: Gateway Cold Start Takes >30s
**Impact:** First health check may fail
**Workaround:** Health check retries 3 times with 10s delay (total 30s)
**Not Critical:** Gateway will eventually pass health check

### Issue: Service URL Propagation Delay
**Impact:** Gateway might try to build before URLs are in Secret Manager
**Workaround:** 1-2 minute wait between workflows is built-in
**Manual Fix:** Re-trigger gateway-deploy if it fails due to missing URLs

### Issue: Terraform State Lock
**Impact:** Can't deploy if state is locked
**Fix:**
```bash
# Check for locks
gsutil ls gs://mindmirror-prod-terraform-state/*.tflock

# If stuck, force unlock (DANGEROUS, ensure no apply running):
cd infra
tofu force-unlock <lock-id>
```

---

## Final Pre-Production Checklist ✅

### Must Complete Before Production:
- [ ] Add 4 missing outputs to `infra/outputs.tf`
- [ ] Test staging end-to-end successfully
- [ ] Create 2 production gateway workflows
- [ ] Update production-deploy.yml (exclude gateway)
- [ ] Update tofu-apply-production.yml (add URL extraction)
- [ ] Create production Secret Manager secret
- [ ] Configure production IAM permissions
- [ ] Set up GitHub production environment
- [ ] Review all workflows with team
- [ ] Schedule deployment window
- [ ] Prepare rollback plan

### Nice to Have:
- [ ] Monitoring dashboards set up
- [ ] Alerting configured
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Runbook reviewed with team

---

## You're Fucking Ready! 🚀

Once you:
1. Fix the 4 missing Terraform outputs
2. Test staging tomorrow (validate end-to-end)
3. Create production workflows
4. Complete Vercel cutover

**You'll be ready to deploy production like a boss.**

The two-phase gateway deployment pattern is solid. Scripts are tested. Staging is your safety net. Production will be smooth as dick. 💪

Questions? I'm here when you need me. Let's make this production deployment perfect. 🔥
