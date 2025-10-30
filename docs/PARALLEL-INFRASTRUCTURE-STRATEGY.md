# Parallel Infrastructure Strategy

**Approach**: Run TWO separate infrastructure deployments side-by-side, validate the new automation, then cutover.

**Key Insight**: Instead of migrating state, we deploy a PARALLEL staging environment with automation, test it thoroughly, then switch traffic when ready.

---

## Architecture: Dual Staging Environments

```
┌─────────────────────────────────────────────────────────────┐
│ CURRENT STATE (Keep Running)                                │
│                                                              │
│  Manual Tofu State                                          │
│    ├─ GCS: mindmirror-tofu-state/envs/default              │
│    ├─ Services: agent-service, journal-service, etc.       │
│    ├─ Domain: *.run.app (current URLs)                     │
│    └─ Status: PRODUCTION TRAFFIC ← Keep this running       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ NEW STATE (Automated)                                        │
│                                                              │
│  GitHub Actions Automated                                    │
│    ├─ GCS: mindmirror-tofu-state/envs/staging              │
│    ├─ Services: agent-service-auto, journal-service-auto   │
│    ├─ Domain: *-auto.run.app (new URLs)                    │
│    └─ Status: TESTING ← Validate here                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CUTOVER (When Ready)                                         │
│                                                              │
│  Option A: Rename services (blue/green)                     │
│    ├─ Stop old services                                     │
│    ├─ Rename new services to old names                      │
│    └─ Update state to match                                 │
│                                                              │
│  Option B: Traffic switch                                   │
│    ├─ Update gateway to point to new services               │
│    ├─ Monitor for issues                                    │
│    └─ Decommission old when stable                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Deploy Parallel "Auto" Stack (1 hour)

### Step 1.1: Create Separate Service Names

Update `infra/staging.auto.tfvars` to use different service names:

```hcl
# infra/staging.auto.tfvars
project_id     = "mindmirror-staging"
region         = "us-east4"
environment    = "staging"

# Use -auto suffix to avoid conflicts
agent_service_name    = "agent-service-auto"
journal_service_name  = "journal-service-auto"
habits_service_name   = "habits-service-auto"
meals_service_name    = "meals-service-auto"
movements_service_name = "movements-service-auto"
practices_service_name = "practices-service-auto"
users_service_name     = "users-service-auto"
gateway_service_name   = "gateway-auto"
celery_worker_name     = "celery-worker-auto"

# Same databases, registries, etc. (shared resources OK)
# Different Cloud Run services (isolated)
```

### Step 1.2: Setup WIF (Same as Before)

```bash
# Follow SAFE-TESTING-STRATEGY.md Phase 1
# Setup WIF pool, provider, service account
# Grant permissions (can be full permissions now - won't touch existing services)
```

### Step 1.3: Initialize New State Path

```bash
cd infra

# Initialize with new backend (envs/staging path)
tofu init -backend-config=staging.backend.hcl -reconfigure

# State is empty - that's OK!
tofu state list
# (empty)

# Plan shows creating NEW services (with -auto suffix)
tofu plan -var-file=staging.auto.tfvars
# Expected: Plan to create agent-service-auto, journal-service-auto, etc.
```

### Step 1.4: Review Plan Carefully

**What you should see**:
```
Plan: 9 to add, 0 to change, 0 to destroy.

  + google_cloud_run_service.agent_service_auto
  + google_cloud_run_service.journal_service_auto
  + ... (all new services with -auto suffix)
```

**What you should NOT see**:
- ❌ Any changes to existing services (agent-service, journal-service, etc.)
- ❌ Any deletions
- ❌ Any modifications to databases, buckets, etc.

**If plan looks safe**, proceed!

### Step 1.5: Apply to Create Parallel Stack

```bash
# First time: Manual apply (not via automation)
cd infra
tofu apply -var-file=staging.auto.tfvars

# Wait 5-10 minutes for services to deploy
```

**Result**: You now have BOTH stacks running:
- Old: `agent-service.run.app` (current production traffic)
- New: `agent-service-auto.run.app` (ready for testing)

---

## Phase 2: Test Parallel Stack (2 hours)

### Step 2.1: Verify New Services Are Healthy

```bash
# List all services
gcloud run services list --project=mindmirror-staging --region=us-east4

# Should see BOTH:
# - agent-service (old)
# - agent-service-auto (new)

# Test new service health
AGENT_AUTO_URL=$(gcloud run services describe agent-service-auto \
  --project=mindmirror-staging \
  --region=us-east4 \
  --format='value(status.url)')

curl $AGENT_AUTO_URL/health
# Expected: 200 OK
```

### Step 2.2: Run Smoke Tests Against New Stack

```bash
# Test each service
for SERVICE in agent-service-auto journal-service-auto gateway-auto; do
  URL=$(gcloud run services describe $SERVICE \
    --project=mindmirror-staging \
    --region=us-east4 \
    --format='value(status.url)')

  echo "Testing $SERVICE at $URL"
  curl -f "$URL/health" || echo "FAILED: $SERVICE"
done
```

### Step 2.3: Test GitHub Actions Automation

Now test the automation against the NEW stack (won't touch old stack):

```bash
# Create test branch
git checkout -b test/parallel-automation

# Make a trivial change to agent service
cd infra/modules/agent_service
# Change a description or annotation

git add infra/
git commit -m "test: automation against parallel stack"
git push origin test/parallel-automation

# Create PR to staging
gh pr create --base staging --title "Test: Parallel stack automation"

# Watch:
# 1. Plan workflow comments on PR
# 2. Plan shows ONLY agent-service-auto changes (not agent-service)
# 3. Merge PR
# 4. Approve staging deployment
# 5. Verify agent-service-auto updates (agent-service unchanged)
```

**Success criteria**:
- ✅ Plan shows only -auto services changing
- ✅ Apply updates -auto services successfully
- ✅ Old services completely untouched
- ✅ Can iterate rapidly without risk

---

## Phase 3: Gradually Migrate Traffic (1-2 weeks)

### Option A: Gateway-Level Traffic Split

**Best for**: Gradual rollout, easy rollback

Update gateway to route some traffic to new services:

```typescript
// mesh/gateway.config.ts or similar
const serviceRoutes = {
  agent: {
    production: 'agent-service.run.app',      // 90% traffic
    canary: 'agent-service-auto.run.app',     // 10% traffic
  },
  journal: {
    production: 'journal-service.run.app',    // 100% traffic
    canary: 'journal-service-auto.run.app',   // 0% traffic (ready when needed)
  }
}

// Gradually increase canary percentage
// Monitor metrics, errors, latency
// Rollback if issues detected
```

**Traffic progression**:
1. Week 1: 10% → new stack
2. Week 2: 50% → new stack (if no issues)
3. Week 3: 100% → new stack

### Option B: Service-by-Service Cutover

**Best for**: Clean separation, full control

Migrate one service at a time:

```bash
# Week 1: Cut over practices service (low risk)
# 1. Update gateway to point to practices-service-auto
# 2. Monitor for 48 hours
# 3. If stable, decommission practices-service (old)

# Week 2: Cut over movements, users services
# Week 3: Cut over meals, habits services
# Week 4: Cut over journal, agent services (highest risk)
# Week 5: Cut over gateway last
```

### Option C: Blue/Green Rename Swap

**Best for**: Instant cutover, instant rollback

```bash
# Prerequisites: New stack fully validated

# 1. Scale old services to 0 (but keep them)
gcloud run services update agent-service \
  --project=mindmirror-staging \
  --region=us-east4 \
  --min-instances=0 \
  --max-instances=0

# 2. Rename new service to old name (DNS swap)
# (This requires manual intervention - Cloud Run doesn't support rename)
# OR update all clients to use new URLs

# 3. Monitor for 24 hours

# 4. If stable, delete old services
tofu state rm module.agent_service.google_cloud_run_service.agent_service
gcloud run services delete agent-service --quiet
```

---

## Phase 4: Decommission Old Stack (1 hour)

Once new stack is stable and handling 100% traffic:

### Step 4.1: Remove Old Services from Tofu

```bash
# Switch back to old state
cd infra
tofu init -reconfigure  # Use old backend

# Remove resources from state (don't delete from GCP yet)
tofu state rm module.agent_service.google_cloud_run_service.agent_service
tofu state rm module.journal_service.google_cloud_run_service.journal_service
# ... for all services

# Verify state no longer manages old services
tofu state list
# Should be empty or only show shared resources
```

### Step 4.2: Manually Delete Old Services (Safe Now)

```bash
# Delete old Cloud Run services manually
gcloud run services delete agent-service \
  --project=mindmirror-staging \
  --region=us-east4 \
  --quiet

# Repeat for all old services
```

### Step 4.3: Rename New Services to Old Names (Optional)

```bash
# If you want clean names without -auto suffix
# (Requires recreating services with new names)

# Update staging.auto.tfvars
agent_service_name = "agent-service"  # Remove -auto suffix

# Apply to recreate with correct name
cd infra
tofu init -backend-config=staging.backend.hcl
tofu apply -var-file=staging.auto.tfvars
```

---

## Cost Impact

**During parallel run**:
- **2x Cloud Run services**: ~$40/month staging (normally $20)
- **Same databases**: No additional cost (shared)
- **Same Artifact Registry**: No additional cost (shared)
- **Total additional cost**: ~$20/month for 1-2 weeks

**After cutover**:
- Cost returns to normal (~$20/month staging)

**ROI**: $20-40 to de-risk a critical infrastructure migration = worth it!

---

## Advantages of Parallel Approach

### vs. State Migration
✅ **Zero risk to current production**
- Old stack completely untouched
- Can't accidentally delete/recreate services
- Easy rollback (just keep using old stack)

✅ **Test automation thoroughly**
- Iterate on new stack without fear
- Break things and learn
- Perfect the workflow before cutover

✅ **Gradual migration**
- Service-by-service cutover
- Traffic splitting for canary testing
- Validate each service independently

✅ **Instant rollback**
- Old stack ready to take traffic back
- Just update gateway routing
- No state restoration needed

### vs. In-Place Update
✅ **No downtime**
- Services deploy independently
- Gateway routes to healthy services
- Blue/green deployment pattern

✅ **Lower stress**
- Take your time
- Test thoroughly
- No rush to complete migration

---

## Rollback Scenarios

### Scenario 1: New Service Fails Health Checks

```bash
# Old service still running - do nothing
# Or update gateway to route to old service
# Investigate and fix new service at your leisure
```

### Scenario 2: Automation Breaks New Service

```bash
# Old service unaffected - traffic continues
# Fix automation and redeploy to new service
# No production impact
```

### Scenario 3: Need to Abandon New Stack

```bash
# Just delete new services
gcloud run services delete agent-service-auto --quiet
# ... for all -auto services

# Old services continue running
# Zero production impact
```

---

## Modified File Changes Needed

### Update `infra/staging.auto.tfvars`

```hcl
# Add -auto suffix to all service names
agent_service_name    = "agent-service-auto"
journal_service_name  = "journal-service-auto"
# ... etc
```

### Update Service Modules (if service_name is hardcoded)

```hcl
# infra/modules/agent_service/main.tf
resource "google_cloud_run_service" "agent_service" {
  name     = var.service_name  # ← Make sure this uses variable, not hardcoded
  # ...
}

# infra/modules/agent_service/variables.tf
variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "agent-service"  # ← This will be overridden by tfvars
}
```

### No Changes Needed to Workflows

The workflows already use `staging.auto.tfvars`, which will deploy the -auto services automatically!

---

## Timeline

**Week 1**: Deploy parallel stack, validate automation
- Day 1-2: Setup WIF, deploy new stack
- Day 3-5: Test automation, iterate on configs
- Day 6-7: Smoke tests, performance validation

**Week 2-3**: Gradual traffic migration
- Start with low-risk services (practices, movements)
- 10% → 50% → 100% traffic to new stack
- Monitor metrics closely

**Week 4**: Decommission old stack
- Verify 100% traffic on new stack
- Remove old services from Tofu state
- Delete old Cloud Run services
- Rename new services (optional)

**Total**: 3-4 weeks for zero-risk migration

---

## Recommended Approach Summary

1. ✅ **Deploy parallel -auto services** (new state path)
2. ✅ **Test automation against -auto services** (break things safely)
3. ✅ **Gradually route traffic** (10% → 100% over 2 weeks)
4. ✅ **Decommission old services** (once stable)
5. ✅ **Repeat for production** (same approach)

**This is the professional way to do infrastructure migrations!** 🎯

Zero downtime, zero risk, full validation before cutover.

Want me to update the service modules to support the `-auto` suffix pattern?
