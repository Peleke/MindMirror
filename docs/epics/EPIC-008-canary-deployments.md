# EPIC-008: Canary Deployments & Traffic Splitting

**Phase:** 3 (Nice-to-Have - Future)
**Priority:** 🟢 Nice-to-Have
**Estimated Duration:** 2 weeks
**Status:** Not Started

## Overview

Implement canary deployment strategy with traffic splitting to progressively roll out changes while monitoring for issues, enabling safer deployments and automatic rollback.

## Business Value

- **Zero-Downtime Deployments**: Users never experience outages
- **Risk Reduction**: Issues affect small % of users initially
- **Faster Recovery**: Automatic rollback on metric degradation
- **Confidence**: Deploy major changes with safety net
- **User Experience**: Gradual rollout = smoother launches

## Current State

- ❌ All-or-nothing deployments
- ❌ Full traffic to new version immediately
- ❌ Manual rollback required
- ✅ Cloud Run keeps previous revisions
- ✅ Health checks exist

## Target State

- ✅ Gradual traffic shifting (5% → 25% → 50% → 100%)
- ✅ Metrics-driven rollout progression
- ✅ Automatic rollback on error spikes
- ✅ Blue-green deployment for instant rollback
- ✅ Canary analysis automation
- ✅ Manual promotion controls

## Technical Approach

### 1. Cloud Run Traffic Splitting
```yaml
# Canary deployment stages:
Stage 1 (Initial):
  - Deploy new revision
  - Route 5% traffic to canary
  - Route 95% traffic to stable
  - Monitor for 30 minutes

Stage 2 (Expand):
  - If metrics good: 25% canary
  - If bad: Rollback to 0%
  - Monitor for 1 hour

Stage 3 (Majority):
  - If metrics good: 50% canary
  - Monitor for 2 hours

Stage 4 (Full):
  - If metrics good: 100% canary
  - Old version becomes backup
```

### 2. Canary Analysis Metrics
```yaml
# Success criteria:
error_rate:
  canary_max: 0.5%
  increase_threshold: 2x stable version

latency_p99:
  canary_max: 2000ms
  increase_threshold: 1.5x stable version

availability:
  canary_min: 99.9%

# Automatic rollback if any threshold exceeded
```

### 3. Traffic Splitting Strategies
```yaml
# By percentage (default):
- 5% → 25% → 50% → 100%

# By user segment:
- Internal team first
- Beta users second
- All users third

# By region:
- US-East first
- Other regions after verification
```

### 4. Implementation Options
```yaml
# Option 1: Cloud Run native
- Use Cloud Run traffic splitting
- Update percentages via gcloud CLI
- Pro: Simple, native integration
- Con: Manual metric checking

# Option 2: Flagger (recommended)
- Kubernetes canary controller
- Automated progressive rollout
- Metrics-driven decisions
- Pro: Fully automated
- Con: Requires Kubernetes

# Option 3: Gateway-level
- Split traffic at API Gateway
- Fine-grained control
- Pro: Works with any backend
- Con: More complex setup
```

### 5. Rollback Automation
```yaml
# Auto-rollback triggers:
- Error rate > 2x stable
- p99 latency > 1.5x stable
- Health check failures
- Manual abort button

# Rollback process:
1. Set canary traffic to 0%
2. All traffic to stable version
3. Create incident issue
4. Alert team
5. Preserve canary for debugging
```

## Success Criteria

- [ ] Canary deployment functional in staging
- [ ] Automatic traffic progression works
- [ ] Auto-rollback triggered successfully
- [ ] Zero-downtime deployment verified
- [ ] Metrics dashboard shows canary health
- [ ] Manual promotion controls available
- [ ] Team performs successful canary deploy

## Dependencies

- EPIC-004: Monitoring & Observability (metrics for canary analysis)
- EPIC-002: Rollback Mechanism (rollback procedures)
- Cloud Run or Kubernetes infrastructure

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Inconsistent user experience during rollout | Medium | Session stickiness, gradual rollout |
| Metrics lag causes slow rollback | High | Real-time metrics, low latency monitoring |
| Database migrations complicate canary | High | Backward-compatible migrations required |
| Stateful services difficult to canary | Medium | External state (Redis, DB), not in-process |

## Stories

- STORY-046: Research canary deployment options
- STORY-047: Implement Cloud Run traffic splitting
- STORY-048: Create canary metrics dashboard
- STORY-049: Build automated rollout progression
- STORY-050: Implement auto-rollback logic
- STORY-051: Add manual promotion controls
- STORY-052: Test canary deployment end-to-end
- STORY-053: Document canary deployment procedures

## Related Epics

- EPIC-004: Monitoring & Observability (canary metrics)
- EPIC-002: Rollback Mechanism (auto-rollback)
- EPIC-007: Feature Flags (canary + flags = powerful)

## Acceptance Criteria

**Epic is complete when:**
1. Canary deployment works in production
2. Traffic automatically progresses 5% → 100%
3. Auto-rollback triggered by metric threshold
4. Zero-downtime verified during deployment
5. Team successfully deploys 3 services via canary
6. Incident response improved (faster rollback)
7. Documentation covers all canary scenarios
