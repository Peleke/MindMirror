# EPIC-002: Automated Rollback & Incident Response

**Phase:** 1 (Critical)
**Priority:** 🔴 Critical - Launch Blocker
**Estimated Duration:** 3 days
**Status:** Not Started

## Overview

Implement one-click rollback capability and automated incident response to minimize downtime and enable rapid recovery from failed deployments.

## Business Value

- **Reduced Downtime**: Rollback in seconds vs. manual emergency deployments
- **User Trust**: Quick recovery from issues maintains user confidence
- **Team Confidence**: Devs ship fearlessly knowing rollback is easy
- **SLA Compliance**: Meet uptime SLAs (99.9% = max 43 minutes downtime/month)
- **Cost Savings**: Reduced incident response time = lower operational costs

## Current State

- ❌ No automated rollback mechanism
- ❌ Manual revert → PR → redeploy required
- ❌ No post-deployment health checks
- ❌ No automated incident creation
- ✅ Cloud Run versions are kept (manual rollback possible)

## Target State

- ✅ One-click rollback via GitHub UI/CLI
- ✅ Automated health checks post-deployment
- ✅ Auto-rollback on health check failures
- ✅ Incident automation (GitHub issue creation)
- ✅ Deployment status dashboard
- ✅ Documented rollback procedures

## Technical Approach

### 1. Health Check System
```yaml
# Post-deploy health checks:
- /health endpoint responds 200 OK
- Service logs show no startup errors
- Gateway can reach service
- Database connections successful
```

### 2. Rollback Workflow
```yaml
# .github/workflows/rollback.yml
on:
  workflow_dispatch:
    inputs:
      service:
        description: 'Service to rollback'
        required: true
      environment:
        description: 'staging or production'
        required: true
      version:
        description: 'Version to rollback to (optional)'
```

### 3. Auto-Rollback Triggers
- Health check failure > 3 attempts
- Error rate > 5% in first 10 minutes
- Manual trigger via GitHub UI

### 4. Incident Response
- Auto-create GitHub issue on rollback
- Notify team via Slack/Discord
- Tag issue with `incident`, `critical`
- Include logs and rollback reason

## Success Criteria

- [ ] Rollback workflow functional for all services
- [ ] Health checks run post-deployment
- [ ] Auto-rollback triggered on health check failure
- [ ] Incident issues created automatically
- [ ] Team performs successful test rollback
- [ ] Rollback time < 2 minutes (vs. 30+ minutes manual)

## Dependencies

- Services must have `/health` endpoints (already exist)
- Cloud Run revision history available

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database migrations can't be rolled back | High | Separate migration rollback procedure |
| Rollback to broken version | Medium | Version selection UI shows health status |
| False positive health checks | Medium | Require 3 consecutive failures before rollback |
| Rollback cascade (multiple services) | Medium | Manual approval for multi-service rollback |

## Stories

- STORY-006: Enhance health check endpoints
- STORY-007: Create rollback GitHub workflow
- STORY-008: Implement post-deploy health checks
- STORY-009: Add auto-rollback on health failures
- STORY-010: Incident automation (issue creation)
- STORY-011: Rollback documentation and runbooks

## Related Epics

- EPIC-004: Monitoring & Observability (metrics inform rollback decisions)
- EPIC-003: Quality Gates (tests prevent need for rollback)

## Acceptance Criteria

**Epic is complete when:**
1. Rollback workflow successfully tested in staging
2. Health check failures trigger auto-rollback
3. Incident issues created with full context
4. Team can rollback any service in < 2 minutes
5. Rollback runbook documented and tested
6. Zero-downtime rollback demonstrated (blue-green or canary)
