# Deployment Workflow Diagrams

## Staging Pipeline (4 Phases - Auto-Approved)

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: Deploy Services to Staging                            │
│ Workflow: Deploy to Staging                                    │
│ Trigger: Push to 'staging' branch                              │
│ Actions:                                                        │
│   1. Build 7 service images (agent, journal, habits, etc.)     │
│   2. Push to mindmirror-69/mindmirror registry                 │
│   3. Update staging.auto.tfvars with new image tags            │
│   4. Commit changes to staging branch                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │ triggers
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: Apply Service Infrastructure                          │
│ Workflow: Tofu Apply - Staging                                 │
│ Trigger: "Deploy to Staging" completes                         │
│ Actions:                                                        │
│   1. Run 'tofu plan' with staging.auto.tfvars                  │
│   2. Auto-approve and apply changes                            │
│   3. Deploy services to Cloud Run                              │
│   4. Save service URLs to Secret Manager                       │
│      Secret: service-urls-staging                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │ triggers
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: Build Gateway with Service URLs                       │
│ Workflow: Deploy Gateway to Staging                            │
│ Trigger: "Tofu Apply - Staging" completes                      │
│ Actions:                                                        │
│   1. Fetch service URLs from service-urls-staging secret       │
│   2. Build gateway image with URLs as build args               │
│   3. Push gateway image to registry                            │
│   4. Update staging.auto.tfvars with gateway image             │
│   5. Commit changes to staging branch                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │ triggers
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: Deploy Gateway                                        │
│ Workflow: Tofu Apply - Gateway (Staging)                       │
│ Trigger: "Deploy Gateway to Staging" completes                 │
│ Actions:                                                        │
│   1. Run 'tofu plan' for gateway only                          │
│   2. Auto-approve and apply                                    │
│   3. Deploy gateway to Cloud Run                               │
│   4. Run health check (3 retries, 10s delay)                   │
└─────────────────────────────────────────────────────────────────┘

✅ All 4 phases auto-approved (no manual intervention)
⏱️  Total time: ~15-20 minutes
```

---

## Production Pipeline (6 Phases - 2 Approval Gates)

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: Deploy Services to Production                         │
│ Workflow: Deploy to Production                                 │
│ Trigger: Push to 'main' branch                                 │
│ Actions:                                                        │
│   1. Build 7 service images                                    │
│   2. Push to mindmirror-prod/mindmirror registry               │
│   3. Update production.auto.tfvars with new image tags         │
│   4. CREATE PR to main branch (not direct commit)              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ MANUAL STEP    │
              │ Review + Merge │
              │ tfvars PR      │
              └────────┬───────┘
                       │ triggers (after merge)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: Apply Service Infrastructure                          │
│ Workflow: Tofu Apply - Production                              │
│ Trigger: PR merged from Phase 1                                │
│ Actions:                                                        │
│   1. Run 'tofu init' with production.backend.hcl               │
│   2. Run 'tofu plan' with production.auto.tfvars               │
│   3. ⏸️  PAUSE FOR APPROVAL (GitHub Environment gate)          │
│       → Go to Actions tab                                       │
│       → Click "Review deployments"                              │
│       → Select "production"                                     │
│       → Click "Approve and deploy"                              │
│   4. Apply infrastructure changes                              │
│   5. Save service URLs to Secret Manager                       │
│      Secret: service-urls-production                           │
│   6. Create GitHub issue: "✅ Production deployment"           │
└──────────────────────┬──────────────────────────────────────────┘
                       │ triggers (after approval + completion)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: Build Gateway with Service URLs                       │
│ Workflow: Deploy Gateway to Production                         │
│ Trigger: "Tofu Apply - Production" completes                   │
│ Actions:                                                        │
│   1. Fetch URLs from service-urls-production secret            │
│   2. Build gateway image with production URLs                  │
│   3. Push gateway image to mindmirror-prod registry            │
│   4. Update production.auto.tfvars with gateway image          │
│   5. CREATE PR to main branch (not direct commit)              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ MANUAL STEP    │
              │ Review + Merge │
              │ gateway PR     │
              └────────┬───────┘
                       │ triggers (after merge)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: Deploy Gateway                                        │
│ Workflow: Tofu Apply - Gateway (Production)                    │
│ Trigger: PR merged from Phase 3                                │
│ Actions:                                                        │
│   1. Run 'tofu init' with production.backend.hcl               │
│   2. Run 'tofu plan' for gateway only                          │
│   3. ⏸️  PAUSE FOR APPROVAL (GitHub Environment gate)          │
│       → Go to Actions tab                                       │
│       → Click "Review deployments"                              │
│       → Select "production"                                     │
│       → Click "Approve and deploy"                              │
│   4. Apply gateway infrastructure                              │
│   5. Deploy gateway to Cloud Run                               │
│   6. Run health check (3 retries, 10s delay)                   │
│   7. Create GitHub issue: "✅ Production gateway deployment"   │
└─────────────────────────────────────────────────────────────────┘

🛡️  2 approval gates (Phase 2 and Phase 4)
📋 2 manual PR reviews (after Phase 1 and Phase 3)
⏱️  Total time: ~25-30 minutes
```

---

## Key Differences: Staging vs Production

| Aspect | Staging | Production |
|--------|---------|------------|
| **Approval Gates** | ❌ None (auto-approved) | ✅ 2 gates (services + gateway) |
| **PR Creation** | Direct commits | Creates PRs for review |
| **Environment** | `environment: staging` not used | `environment: production` required |
| **Service Names** | `{service}-staging` | `{service}` (bare names) |
| **Project** | `mindmirror-69` | `mindmirror-prod` |
| **Branch** | `staging` | `main` |
| **Backend Config** | No backend in gateway workflows | `production.backend.hcl` |
| **Issue Tracking** | Minimal | Comprehensive (success + failure) |

---

## Approval Flow Visualization

```
Production Deployment Approval Process
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Services Deployment:
  Push to main → Build services → Create PR
       ↓
  [Manual PR Review]
       ↓
  Merge PR → Tofu Plan
       ↓
  ⏸️  [APPROVAL GATE #1] ← You click "Approve" in GitHub Actions
       ↓
  Deploy services → Save URLs → Create success issue

Gateway Deployment:
  Build gateway → Create PR
       ↓
  [Manual PR Review]
       ↓
  Merge PR → Tofu Plan
       ↓
  ⏸️  [APPROVAL GATE #2] ← You click "Approve" in GitHub Actions
       ↓
  Deploy gateway → Health check → Create success issue
```

---

## Secrets Flow Diagram

```
Service Deployment (Phase 2)
━━━━━━━━━━━━━━━━━━━━━━━━
1. Services deploy to Cloud Run
2. Each service gets a URL:
   - https://agent-service-{hash}.run.app
   - https://journal-service-{hash}.run.app
   - ... (7 services total)

3. Workflow saves URLs to Secret Manager:
   Secret: service-urls-{environment}
   Format: {
     "agent_service_url": "https://...",
     "journal_service_url": "https://...",
     ...
   }

                    ↓

Gateway Build (Phase 3)
━━━━━━━━━━━━━━━━━━━━
1. Workflow fetches secret: service-urls-{environment}
2. Parses JSON to extract individual URLs
3. Passes URLs as Docker build args:
   --build-arg AGENT_SERVICE_URL=https://...
   --build-arg JOURNAL_SERVICE_URL=https://...
   ...
4. Gateway hardcodes these URLs in mesh config
5. Gateway image pushed to registry

                    ↓

Gateway Deployment (Phase 4)
━━━━━━━━━━━━━━━━━━━━━━━━
1. Gateway deployed with baked-in service URLs
2. Gateway can now federate all microservices
3. Health check verifies federation works
```

---

## Monitoring During Deployment

```
GitHub Actions Tab
━━━━━━━━━━━━━━━━━━
Watch: https://github.com/{org}/MindMirror/actions

Look for:
  🟢 Green checkmarks = Success
  🟡 Yellow dot = In progress
  🟠 Orange "Review" button = Approval needed
  🔴 Red X = Failed

Click into workflow to see:
  - Real-time logs for each step
  - Approval buttons (when paused)
  - Deployment summaries

GCP Console
━━━━━━━━━━
Cloud Run: https://console.cloud.google.com/run?project=mindmirror-prod

Look for:
  - New revisions deploying
  - Traffic shifting to new revision
  - Service URLs (click service to see URL)

Secret Manager: https://console.cloud.google.com/security/secret-manager

Look for:
  - service-urls-staging (created by staging)
  - service-urls-production (created by production)
```

---

## Rollback Visualization

```
If Deployment Fails
━━━━━━━━━━━━━━━━━━

Option 1: Git Revert (Recommended)
┌────────────────────────────────────────┐
│ cd infra                               │
│ git checkout HEAD~1 -- production.auto.tfvars
│ git commit -m "rollback: production"  │
│ git push origin main                   │
│ → Creates new PR                       │
│ → Merge PR                             │
│ → Approve rollback in Actions          │
└────────────────────────────────────────┘

Option 2: Manual GCP Deploy (Emergency)
┌────────────────────────────────────────┐
│ gcloud run deploy gateway \            │
│   --image=KNOWN_GOOD_IMAGE \           │
│   --region=us-east4 \                  │
│   --project=mindmirror-prod            │
└────────────────────────────────────────┘
  Bypasses all workflows
  Use only in emergency
```

---

## Quick Reference: What Gets Created

```
Per Environment, Per Deployment:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Artifact Registry (Container Images):
  7 service images: agent-service, journal-service, etc.
  1 gateway image: mesh

Cloud Run Services:
  7 backend services
  1 gateway service

Secret Manager:
  1 secret: service-urls-{environment}

GitHub:
  2 PRs (services + gateway tfvars updates)
  2 Issues (success/failure notifications)

Git Commits:
  2 commits to main (merged PRs)
  Updated: production.auto.tfvars
```
