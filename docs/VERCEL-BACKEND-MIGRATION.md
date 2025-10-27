# Vercel Backend Migration Runbook

**Status**: Ready to Execute (After staging/production deployments validated)
**Priority**: High (Required for production launch)
**Owner**: DevOps/Frontend
**Created**: 2025-10-27
**Dependencies**: GitOps workflows validated, staging + production deployed

---

## Overview

Migrate Vercel deployments to point to new GCP Cloud Run backends instead of legacy infrastructure.

**Current State**:
- Vercel deployments point to old/legacy backend URLs
- Staging and production environments not properly separated in Vercel

**Target State**:
- Vercel staging → Cloud Run staging (mindmirror-69)
- Vercel production → Cloud Run production (mindmirror-prod)
- Clean environment separation with proper secrets

---

## Prerequisites

### Before Starting

- [x] GitOps workflows validated (tofu-plan.yml working)
- [ ] Staging deployment successful (services + gateway deployed to mindmirror-69)
- [ ] Production deployment successful (services + gateway deployed to mindmirror-prod)
- [ ] Cloud Run service URLs documented
- [ ] Vercel project access verified

### Required Information

Gather these before starting:

**Staging Cloud Run URLs**:
```bash
# Get staging service URLs
gcloud run services list \
  --project=mindmirror-69 \
  --region=us-east4 \
  --format="table(metadata.name,status.url)"

# Key URL: Gateway
STAGING_GATEWAY_URL=$(gcloud run services describe gateway \
  --project=mindmirror-69 \
  --region=us-east4 \
  --format="value(status.url)")

echo "Staging Gateway: $STAGING_GATEWAY_URL"
```

**Production Cloud Run URLs**:
```bash
# Get production service URLs
gcloud run services list \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="table(metadata.name,status.url)"

# Key URL: Gateway
PRODUCTION_GATEWAY_URL=$(gcloud run services describe gateway \
  --project=mindmirror-prod \
  --region=us-east4 \
  --format="value(status.url)")

echo "Production Gateway: $PRODUCTION_GATEWAY_URL"
```

---

## Phase 1: Update Vercel Staging Environment

### Step 1: Verify Current Vercel Configuration

```bash
# List Vercel projects
vercel ls

# Get current environment variables
vercel env ls --environment=preview
vercel env ls --environment=development
```

### Step 2: Update Staging Environment Variables

**Via Vercel Dashboard** (Recommended):

1. Go to: https://vercel.com/[your-team]/mindmirror/settings/environment-variables

2. **Update/Add these variables for Preview + Development**:

   ```bash
   # GraphQL Gateway
   NEXT_PUBLIC_GATEWAY_URL = https://gateway-[hash].run.app/graphql

   # Supabase (Staging)
   NEXT_PUBLIC_SUPABASE_URL = https://[staging-project].supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY = [staging-anon-key]

   # App Mode
   NEXT_PUBLIC_APP_MODE = demo
   NEXT_PUBLIC_INSIGHT_TIMEOUT = 240000
   ```

**Via Vercel CLI** (Alternative):

```bash
# Set staging gateway URL for preview/development
vercel env add NEXT_PUBLIC_GATEWAY_URL preview development
# When prompted, paste: https://gateway-[hash].run.app/graphql

# Update Supabase for staging
vercel env add NEXT_PUBLIC_SUPABASE_URL preview development
# Paste staging Supabase URL

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY preview development
# Paste staging anon key
```

### Step 3: Test Staging Deployment

```bash
# Trigger new deployment to preview
git push origin staging

# Or manually trigger
vercel --prod=false

# Verify deployment
vercel ls
# Click preview URL and test:
# 1. GraphQL queries work
# 2. Supabase auth works
# 3. All features functional
```

### Step 4: Validate Staging

**Manual Testing Checklist**:
- [ ] Preview deployment loads without errors
- [ ] GraphQL gateway reachable (`NEXT_PUBLIC_GATEWAY_URL`)
- [ ] Can query GraphQL endpoint
- [ ] Supabase authentication works
- [ ] Journal entries fetch correctly
- [ ] Agent conversations work
- [ ] All microservices accessible via gateway

**Automated Validation**:
```bash
# Test gateway connectivity
curl -X POST https://gateway-staging.run.app/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'

# Should return: {"data":{"__typename":"Query"}}
```

---

## Phase 2: Update Vercel Production Environment

### Step 1: Create Production Deployment Plan

**IMPORTANT**: Production changes require careful coordination.

**Pre-deployment Checklist**:
- [ ] Staging fully validated (all features working)
- [ ] Production Cloud Run services deployed and healthy
- [ ] Production gateway verified
- [ ] Rollback plan documented
- [ ] Monitoring/alerting ready

### Step 2: Update Production Environment Variables

**Via Vercel Dashboard**:

1. Go to: https://vercel.com/[your-team]/mindmirror/settings/environment-variables

2. **Update these variables for Production ONLY**:

   ```bash
   # GraphQL Gateway (Production)
   NEXT_PUBLIC_GATEWAY_URL = https://gateway-[prod-hash].run.app/graphql

   # Supabase (Production)
   NEXT_PUBLIC_SUPABASE_URL = https://[production-project].supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY = [production-anon-key]

   # App Mode
   NEXT_PUBLIC_APP_MODE = demo
   NEXT_PUBLIC_INSIGHT_TIMEOUT = 240000
   ```

**Via Vercel CLI**:

```bash
# Set production gateway URL
vercel env add NEXT_PUBLIC_GATEWAY_URL production
# Paste: https://gateway-[prod-hash].run.app/graphql

# Update Supabase for production
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# Paste production Supabase URL

vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
# Paste production anon key
```

### Step 3: Deploy to Production

**Option A: Gradual Rollout** (Recommended)

```bash
# 1. Deploy to production (but don't promote yet)
git checkout main
git pull origin main
vercel --prod

# 2. Get deployment URL (not promoted)
# Test thoroughly on deployment URL

# 3. If everything works, promote
vercel promote [deployment-url]
```

**Option B: Direct Deploy**

```bash
# Deploy directly to production (uses env vars immediately)
git checkout main
vercel --prod

# Monitor for issues
```

### Step 4: Validate Production

**Critical Path Testing**:
- [ ] Production deployment loads
- [ ] GraphQL gateway responds
- [ ] Authentication works
- [ ] User journaling works
- [ ] Agent conversations work
- [ ] All critical features functional
- [ ] No console errors
- [ ] Performance acceptable

**Monitoring**:
```bash
# Watch Cloud Run logs
gcloud logging tail "resource.type=cloud_run_revision" \
  --project=mindmirror-prod \
  --format=json

# Monitor gateway specifically
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=gateway" \
  --project=mindmirror-prod
```

---

## Phase 3: Cleanup & Documentation

### Step 1: Remove Old Environment Variables

After successful migration:

```bash
# List all environment variables
vercel env ls

# Remove old/legacy backend URLs
vercel env rm OLD_BACKEND_URL production preview development

# Remove deprecated variables
vercel env rm LEGACY_API_URL production preview development
```

### Step 2: Update Documentation

Update these files:

**CLAUDE.md**:
```markdown
## Vercel Deployments

### Environment Configuration

**Staging** (Preview + Development):
- Gateway: https://gateway-staging.run.app/graphql
- Supabase: [staging project]

**Production**:
- Gateway: https://gateway-production.run.app/graphql
- Supabase: [production project]

### Deployment Process

1. Push to `staging` branch → Vercel preview deployment
2. Merge to `main` → Vercel production deployment
3. Environment variables automatically injected based on environment
```

**README.md**:
```markdown
## Frontend Deployment

Vercel automatically deploys:
- Staging: Connected to Cloud Run staging (mindmirror-69)
- Production: Connected to Cloud Run production (mindmirror-prod)

Environment variables managed via Vercel dashboard.
```

### Step 3: Verify Environment Separation

**Staging should use**:
- ✅ mindmirror-69 Cloud Run services
- ✅ Staging Supabase project
- ✅ Staging gateway

**Production should use**:
- ✅ mindmirror-prod Cloud Run services
- ✅ Production Supabase project
- ✅ Production gateway

**No cross-environment contamination**.

---

## Rollback Plan

### If Staging Breaks

```bash
# Revert to old environment variables
vercel env add NEXT_PUBLIC_GATEWAY_URL preview development
# Paste old/legacy URL

# Redeploy
vercel --prod=false
```

### If Production Breaks

**Immediate Rollback**:

```bash
# Option 1: Rollback to previous deployment
vercel rollback

# Option 2: Revert environment variables
vercel env add NEXT_PUBLIC_GATEWAY_URL production
# Paste old production URL

# Redeploy with old config
vercel --prod
```

**Communication**:
- Update status page if available
- Notify team via Slack
- Document incident for post-mortem

---

## Environment Variables Reference

### Full Staging Configuration

```env
# Vercel Preview + Development Environments

# GraphQL
NEXT_PUBLIC_GATEWAY_URL=https://gateway-[staging-hash].run.app/graphql

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://[staging-project].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[staging-key]

# App Config
NEXT_PUBLIC_APP_MODE=demo
NEXT_PUBLIC_INSIGHT_TIMEOUT=240000
```

### Full Production Configuration

```env
# Vercel Production Environment

# GraphQL
NEXT_PUBLIC_GATEWAY_URL=https://gateway-[production-hash].run.app/graphql

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://[production-project].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[production-key]

# App Config
NEXT_PUBLIC_APP_MODE=demo
NEXT_PUBLIC_INSIGHT_TIMEOUT=240000
```

---

## Verification Commands

### Test Gateway Connectivity

```bash
# Staging
curl -X POST https://gateway-staging.run.app/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}' | jq

# Production
curl -X POST https://gateway-production.run.app/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}' | jq
```

### Test Authenticated Requests

```bash
# Get auth token from Supabase
TOKEN="[your-jwt-token]"

# Test authenticated query
curl -X POST https://gateway-staging.run.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "{ journalEntries { id } }"}' | jq
```

### Verify Vercel Build

```bash
# Check build logs
vercel logs [deployment-url]

# Verify environment variables in build
# Look for: "NEXT_PUBLIC_GATEWAY_URL" in logs
```

---

## Timeline & Execution

### Recommended Execution Order

**Phase 1: Staging Migration** (Day 1)
- ⏰ Duration: 1-2 hours
- 🎯 Goal: Staging Vercel → Cloud Run staging
- ✅ Low risk (preview environment)

**Testing Period** (Days 2-3)
- ⏰ Duration: 2 days
- 🎯 Goal: Validate staging thoroughly
- ✅ Catch any issues before production

**Phase 2: Production Migration** (Day 4)
- ⏰ Duration: 2-4 hours
- 🎯 Goal: Production Vercel → Cloud Run production
- ⚠️ High risk (production environment)
- 📅 Schedule during low-traffic window

**Phase 3: Cleanup** (Day 5)
- ⏰ Duration: 1 hour
- 🎯 Goal: Remove legacy config, update docs

### Parallel Work Streams

While Vercel migration is happening:

**Stream 1: Vercel Migration** (Primary focus)
- Frontend team: Execute migration
- DevOps team: Monitor Cloud Run

**Stream 2: User Onboarding** (Parallel slow-burn)
- Product team: Begin user recruitment
- Marketing team: Prepare materials
- Support team: Documentation updates

**Stream 3: Hive Optimization** (Background)
- Backend team: Phase 1-2 of Hive setup
- No production impact
- Can run concurrently with onboarding

---

## Success Metrics

### Technical Metrics
- ✅ Zero downtime during migration
- ✅ Response times < 500ms (gateway)
- ✅ 100% of features working post-migration
- ✅ Zero error spike in logs
- ✅ All environments properly separated

### Business Metrics
- ✅ No user-facing issues reported
- ✅ Staging validated before production
- ✅ Rollback plan tested (if needed)
- ✅ Team trained on new architecture

---

## Contact & Escalation

### If Things Go Wrong

**Critical Issues** (Production down):
1. Execute rollback immediately
2. Notify team lead
3. Check Cloud Run service health
4. Review logs for errors

**Non-Critical Issues** (Degraded performance):
1. Document the issue
2. Check monitoring/logs
3. Evaluate if rollback needed
4. Fix forward if possible

### Key Commands for Troubleshooting

```bash
# Check Cloud Run service health
gcloud run services describe gateway \
  --project=mindmirror-prod \
  --region=us-east4

# View recent logs
gcloud logging tail "resource.type=cloud_run_revision" \
  --project=mindmirror-prod \
  --limit=50

# Check Vercel deployment status
vercel inspect [deployment-url]

# View Vercel logs
vercel logs [deployment-url] --follow
```

---

## Post-Migration Checklist

After successful migration:

- [ ] Staging Vercel → Cloud Run staging (validated)
- [ ] Production Vercel → Cloud Run production (validated)
- [ ] Old environment variables removed
- [ ] Documentation updated (CLAUDE.md, README.md)
- [ ] Team trained on new architecture
- [ ] Monitoring configured for new backends
- [ ] Rollback plan documented and tested
- [ ] Post-migration retrospective scheduled

---

**Status**: Ready to execute after GitOps validation complete

**Next Steps**:
1. ✅ Complete staging deployment via GitOps
2. ✅ Complete production deployment via GitOps
3. ✅ Gather Cloud Run service URLs
4. ✅ Execute Phase 1 (Staging migration)
5. ✅ Test thoroughly for 2 days
6. ✅ Execute Phase 2 (Production migration)
7. ✅ Begin user onboarding + Hive optimization in parallel
