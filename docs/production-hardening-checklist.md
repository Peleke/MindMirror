# Production Hardening Checklist

**Timeline**: 6 weeks to production (end of 2025)
**Approach**: Phased implementation with validation gates
**Reference**: See `docs/infra-production-audit.md` for detailed gap analysis

---

## Phase 1: Pre-Production Critical (Week 1-2)

**Goal**: Make infrastructure secure enough for production launch

### Security - IAM and Access Control

- [ ] **Remove public access from backend services** (2-3 hours)
  - [ ] Remove `allUsers` IAM binding from agent_service
  - [ ] Remove `allUsers` IAM binding from journal_service
  - [ ] Remove `allUsers` IAM binding from habits_service
  - [ ] Remove `allUsers` IAM binding from meals_service
  - [ ] Remove `allUsers` IAM binding from movements_service
  - [ ] Remove `allUsers` IAM binding from practices_service
  - [ ] Remove `allUsers` IAM binding from users_service
  - [ ] Remove `allUsers` IAM binding from celery_worker_web
  - [ ] Keep `allUsers` ONLY on gateway (public entry point)
  - **Verification**: `curl https://agent-service-xxx.run.app/health` should return 403 Forbidden

- [ ] **Add gateway-only access to backend services** (2-3 hours)
  - [ ] Create `gateway_service_account_email` variable in `infra/variables.tf`
  - [ ] Add gateway IAM binding to agent_service module
  - [ ] Add gateway IAM binding to journal_service module
  - [ ] Add gateway IAM binding to habits_service module
  - [ ] Add gateway IAM binding to meals_service module
  - [ ] Add gateway IAM binding to movements_service module
  - [ ] Add gateway IAM binding to practices_service module
  - [ ] Add gateway IAM binding to users_service module
  - [ ] Add gateway IAM binding to celery_worker_web module
  - **Verification**: Gateway can still call backend services, external clients cannot

- [ ] **Narrow IAM permissions to resource-level** (3-4 hours)
  - [ ] Replace project-level `secretmanager.secretAccessor` with per-secret IAM
  - [ ] Replace project-level `run.invoker` with per-service IAM
  - [ ] Replace project-level `storage.objectAdmin` with per-bucket IAM
  - [ ] Document which secrets each service needs
  - [ ] Grant only necessary secret permissions per service
  - **Verification**: `gcloud iam service-accounts get-iam-policy ...` shows resource-specific bindings

### Architecture - Cloud Run v2 Pilot

- [ ] **Migrate one service to Cloud Run v2 (pilot)** (1 day)
  - [ ] Choose pilot service (recommend: practices_service - simple, low-risk)
  - [ ] Create new v2 module: `infra/modules/practices/main_v2.tf`
  - [ ] Update resource type: `google_cloud_run_v2_service`
  - [ ] Update template structure (remove `spec`, use direct `containers`)
  - [ ] Update IAM binding: `google_cloud_run_v2_service_iam_member`
  - [ ] Test in staging: `tofu plan -var-file=staging.auto.tfvars`
  - [ ] Apply to staging: `tofu apply -var-file=staging.auto.tfvars`
  - **Verification**: Service responds to health checks, GraphQL queries work

- [ ] **Test v2 migration thoroughly** (2 hours)
  - [ ] Health check endpoint returns 200 OK
  - [ ] GraphQL gateway can query the service
  - [ ] Service can access database
  - [ ] Service can access secrets
  - [ ] Logs appear in Cloud Logging
  - [ ] Cold start performance acceptable
  - [ ] Document any issues or blockers
  - **Verification**: All integration tests pass in staging

### Phase 1 Validation Gate

**Before proceeding to Phase 2**:
- ✅ All backend services reject unauthenticated requests (403 Forbidden)
- ✅ Gateway can successfully call all backend services
- ✅ At least 1 service successfully migrated to Cloud Run v2 in staging
- ✅ IAM permissions narrowed (no project-level broad grants)
- ✅ Zero production deployment issues from changes

**Rollback Plan**: Revert Tofu changes, redeploy previous version via Terrateam

---

## Phase 2: Production Hardening (Week 3-4)

**Goal**: Complete v2 migration and add networking layer

### Architecture - Complete Cloud Run v2 Migration

- [ ] **Migrate remaining 7 services to Cloud Run v2** (1-2 weeks)
  - [ ] Migrate agent_service (AI/embeddings, complex)
  - [ ] Migrate journal_service (medium complexity)
  - [ ] Migrate habits_service (simple)
  - [ ] Migrate meals_service (simple)
  - [ ] Migrate movements_service (simple)
  - [ ] Migrate users_service (simple)
  - [ ] Migrate gateway (critical path, test extensively)
  - [ ] Migrate celery_worker_web (background tasks, Pub/Sub integration)
  - **Strategy**: One service per day, test in staging before production
  - **Verification**: All 8 services using `google_cloud_run_v2_service`

- [ ] **Update all IAM bindings for v2** (2-3 hours)
  - [ ] Replace all `google_cloud_run_service_iam_member` with `google_cloud_run_v2_service_iam_member`
  - [ ] Verify permissions still work after migration
  - **Verification**: `tofu plan` shows no IAM changes (already migrated)

### Security - Secret Volumes (requires Cloud Run v2)

- [ ] **Implement secret volume mounts** (1-2 days)
  - [ ] Create volume definitions in each service module
  - [ ] Map secrets to volume paths (e.g., `/secrets/DATABASE_URL`)
  - [ ] Update env vars to point to files (e.g., `DATABASE_URL_FILE=/secrets/DATABASE_URL`)
  - [ ] Update application code to support reading secrets from files
  - [ ] Test in staging with volume-mounted secrets
  - [ ] Document secret file structure
  - **Verification**: Secrets not visible in Cloud Console env vars tab

- [ ] **Application code changes for secret files** (1-2 days)
  - [ ] Update `shared/secrets.py` to read from files
  - [ ] Update agent_service to use file-based secrets
  - [ ] Update journal_service to use file-based secrets
  - [ ] Update all 8 services to use file-based secrets
  - [ ] Add fallback to env vars for local development
  - **Verification**: Services start successfully, can access database/Redis/APIs

### Networking - VPC Setup

- [ ] **Create VPC network** (4-6 hours)
  - [ ] Create `infra/networking.tf` with VPC resources
  - [ ] Define VPC network: `google_compute_network.mindmirror`
  - [ ] Define subnet: `google_compute_subnetwork.cloudrun` (10.0.0.0/24)
  - [ ] Enable Private Google Access on subnet
  - [ ] Create VPC Access Connector: `google_vpc_access_connector.connector`
  - [ ] Define firewall rules for internal traffic
  - [ ] Test in staging: `tofu plan -var-file=staging.auto.tfvars`
  - **Verification**: VPC Connector shows "Ready" status in Cloud Console

- [ ] **Configure Cloud Run services for VPC** (2-3 hours)
  - [ ] Add `vpc_access` block to all Cloud Run v2 services
  - [ ] Set connector reference
  - [ ] Set egress policy: `PRIVATE_RANGES_ONLY` (VPC traffic through VPC, public through internet)
  - [ ] Test one service first (practices), then migrate others
  - **Verification**: Services can still access external APIs (Supabase, Qdrant, OpenAI)

- [ ] **Configure internal ingress for backend services** (2-3 hours)
  - [ ] Set `ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"` for backend services
  - [ ] Keep `ingress = "INGRESS_TRAFFIC_ALL"` for gateway only
  - [ ] Verify backend services have no public URL
  - [ ] Verify gateway can still reach backend services via internal URLs
  - **Verification**: `curl https://agent-service-xxx.run.app` fails (no public endpoint)

### Observability - Monitoring and Alerting

- [ ] **Setup uptime checks** (1 day)
  - [ ] Create uptime check for gateway `/healthcheck`
  - [ ] Create uptime check for web app (if applicable)
  - [ ] Configure check frequency (60 seconds)
  - [ ] Configure alerting on check failures
  - **Verification**: Uptime checks show green status in Cloud Console

- [ ] **Create alert policies** (1 day)
  - [ ] Alert on gateway downtime (uptime check failed)
  - [ ] Alert on high error rate (>10 errors/min)
  - [ ] Alert on high latency (p95 > 2 seconds)
  - [ ] Alert on low instance count (all services scaled to zero)
  - [ ] Configure notification channels (email, Slack, PagerDuty)
  - **Verification**: Test alert by manually triggering condition

- [ ] **Create log-based metrics** (2-3 hours)
  - [ ] Error rate metric (severity >= ERROR)
  - [ ] Request latency metric (p50, p95, p99)
  - [ ] Database query duration metric
  - [ ] Celery task failure metric
  - **Verification**: Metrics visible in Cloud Monitoring dashboards

- [ ] **Create monitoring dashboards** (2-3 hours)
  - [ ] Service health dashboard (uptime, error rate, latency)
  - [ ] Infrastructure dashboard (CPU, memory, instance count)
  - [ ] Cost dashboard (Cloud Run usage, Artifact Registry storage)
  - **Verification**: Dashboards show live data from staging

### Phase 2 Validation Gate

**Before proceeding to Phase 3**:
- ✅ All 8 services migrated to Cloud Run v2 in staging
- ✅ All 8 services migrated to Cloud Run v2 in production
- ✅ Secrets loaded via volume mounts (not env vars)
- ✅ VPC networking active and functional
- ✅ Backend services use internal ingress only
- ✅ Monitoring and alerting configured
- ✅ Zero production incidents from changes

**Rollback Plan**: VPC changes are additive (safe to rollback), v2 migration requires Tofu state manipulation

---

## Phase 3: Polish and Optimization (Week 5-6)

**Goal**: Cost optimization and operational maturity

### Resource Management

- [ ] **Configure autoscaling limits** (1-2 hours)
  - [ ] Set `minScale` per environment (staging: 0, production: 1-2)
  - [ ] Set `maxScale` globally (10 instances per service)
  - [ ] Enable CPU throttling control: `cpu-throttling = "false"` (always-allocated CPU)
  - [ ] Enable startup CPU boost: `startup-cpu-boost = "true"` (faster cold starts)
  - **Verification**: `tofu plan` shows autoscaling annotations

- [ ] **Right-size CPU/memory per service** (ongoing)
  - [ ] Monitor actual usage in staging for 1-2 weeks
  - [ ] Collect p95 CPU and memory metrics
  - [ ] Right-size based on actual usage + 20-30% headroom
  - [ ] Document resource sizing decisions
  - [ ] Agent service: 2 CPU / 2Gi (AI-intensive)
  - [ ] Gateway: 1 CPU / 512Mi (lightweight proxy)
  - [ ] Other services: 1 CPU / 512Mi (standard)
  - **Verification**: No OOM errors, acceptable latency, cost reduction

### Observability - Structured Logging

- [ ] **Implement structured logging** (2-3 days)
  - [ ] Add `json_logging` library to Python services
  - [ ] Update logging configuration to output JSON
  - [ ] Add correlation IDs to all logs (trace requests across services)
  - [ ] Add structured fields: `user_id`, `request_id`, `service_name`
  - [ ] Test log querying in Cloud Logging
  - [ ] Document structured logging patterns
  - **Verification**: Logs queryable by structured fields

### Infrastructure - State Management

- [ ] **Separate state backends per environment** (1 hour)
  - [ ] Create backend config files: `backend-staging.hcl`, `backend-production.hcl`
  - [ ] Create separate state buckets: `mindmirror-staging-tofu-state`, `mindmirror-production-tofu-state`
  - [ ] Remove hardcoded backend from `versions.tf`
  - [ ] Update Terrateam config to use backend configs
  - [ ] Document backend initialization process
  - **Verification**: Staging and production use separate state buckets

### Documentation

- [ ] **Create operational runbooks** (2-3 days)
  - [ ] Service deployment runbook (Terrateam workflow)
  - [ ] Incident response runbook (rollback procedures)
  - [ ] Scaling runbook (when to adjust min/max instances)
  - [ ] Secret rotation runbook (how to update secrets)
  - [ ] Gateway composition runbook (schema updates)
  - [ ] Database migration runbook (Alembic procedures)
  - **Verification**: Team can execute runbooks without external help

- [ ] **Update architecture documentation** (1 day)
  - [ ] Update `CLAUDE.md` with production architecture
  - [ ] Document VPC networking topology
  - [ ] Document secret management approach
  - [ ] Document monitoring and alerting strategy
  - [ ] Create architecture diagrams (draw.io or Mermaid)
  - **Verification**: New team member can understand architecture from docs

### Phase 3 Validation Gate

**Production Ready Criteria**:
- ✅ Autoscaling configured and tested
- ✅ Resources right-sized based on metrics
- ✅ Structured logging implemented
- ✅ Separate state backends per environment
- ✅ Operational runbooks complete
- ✅ Architecture documentation current
- ✅ Team trained on runbooks and procedures

**Production Launch Approval**: Review checklist with team, get sign-off from stakeholders

---

## Workload Identity Federation (Parallel Track)

**Goal**: Replace service account keys with keyless authentication

**Timeline**: Can be done in parallel with Phase 1-3

- [ ] **Setup WIF for staging** (2-3 hours)
  - [ ] Create workload identity pool: `github-pool`
  - [ ] Create OIDC provider: `github-oidc`
  - [ ] Bind staging service account to pool
  - [ ] Update `.github/workflows/staging-deploy.yml`
  - [ ] Test staging deployment with WIF
  - **Verification**: Staging deploys without `GCP_STAGING_SA_KEY` secret

- [ ] **Setup WIF for production** (2-3 hours)
  - [ ] Create workload identity pool: `github-pool` (in production project)
  - [ ] Create OIDC provider: `github-oidc`
  - [ ] Bind production service account to pool
  - [ ] Update `.github/workflows/production-deploy.yml`
  - [ ] Test production deployment with WIF
  - **Verification**: Production deploys without `GCP_PRODUCTION_SA_KEY` secret

- [ ] **Cleanup service account keys** (30 minutes)
  - [ ] Delete GitHub secret: `GCP_STAGING_SA_KEY`
  - [ ] Delete GitHub secret: `GCP_PRODUCTION_SA_KEY`
  - [ ] Delete user-managed keys from staging SA
  - [ ] Delete user-managed keys from production SA
  - **Verification**: No user-managed keys exist for GitHub Actions SAs

**Reference**: See `docs/wif-setup.md` for detailed setup guide

---

## Success Metrics

### Week 2 Checkpoint (Phase 1 Complete)
- [ ] Backend services reject public access (100% success rate)
- [ ] Gateway can call backend services (100% success rate)
- [ ] 1 service migrated to Cloud Run v2 (practices_service)
- [ ] IAM permissions narrowed (0 project-level grants for services)

### Week 4 Checkpoint (Phase 2 Complete)
- [ ] All 8 services on Cloud Run v2 (100% migration)
- [ ] Secrets via volume mounts (0 secrets in env vars)
- [ ] VPC networking active (100% internal traffic)
- [ ] Monitoring configured (uptime checks + alerts)
- [ ] 0 production incidents from hardening changes

### Week 6 Checkpoint (Phase 3 Complete)
- [ ] Autoscaling limits configured (all services)
- [ ] Resources right-sized (cost reduction achieved)
- [ ] Structured logging implemented (all services)
- [ ] Operational runbooks complete (6+ runbooks)
- [ ] Team trained and ready for production support

### Production Launch Criteria
- ✅ All Phase 1, 2, 3 checkpoints met
- ✅ Workload Identity Federation active (no SA keys)
- ✅ Production environment deployed and stable for 1 week
- ✅ Load testing completed (can handle expected traffic)
- ✅ Incident response tested (rollback procedures validated)
- ✅ Stakeholder approval obtained

---

## Risk Management

### High-Risk Changes
1. **Cloud Run v2 migration**: Breaking change, requires careful testing
2. **VPC networking**: Can break external API access if misconfigured
3. **Secret volume mounts**: Requires application code changes

**Mitigation**:
- Test each change in staging first
- Migrate one service at a time (not big-bang)
- Have rollback plan ready
- Monitor closely during and after changes

### Medium-Risk Changes
1. **IAM permission narrowing**: Could break service-to-service calls
2. **Internal ingress**: Could break health checks or monitoring

**Mitigation**:
- Verify integrations after each change
- Test extensively in staging
- Deploy during low-traffic periods

### Low-Risk Changes
1. **Autoscaling limits**: Can be adjusted without downtime
2. **Structured logging**: Additive change, no breaking impact
3. **WIF**: Can coexist with SA keys during migration

**Mitigation**:
- Deploy during business hours (easy to monitor)
- Have team available for quick fixes

---

## Rollback Procedures

### Rollback Cloud Run v2 Migration
```bash
# Revert to previous Tofu state
tofu state pull > backup.tfstate
tofu state rm google_cloud_run_v2_service.SERVICENAME
tofu import google_cloud_run_service.SERVICENAME projects/PROJECT/locations/REGION/services/SERVICENAME
tofu apply -var-file=staging.auto.tfvars
```

### Rollback VPC Networking
```bash
# Remove vpc_access block from service modules
# Apply changes
tofu apply -var-file=staging.auto.tfvars

# Delete VPC resources (safe, services will use public internet)
tofu destroy -target=google_vpc_access_connector.connector
tofu destroy -target=google_compute_subnetwork.cloudrun
tofu destroy -target=google_compute_network.mindmirror
```

### Rollback IAM Changes
```bash
# Restore public access (emergency only)
gcloud run services add-iam-policy-binding SERVICENAME \
  --region=us-east4 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Rollback WIF
```bash
# Restore SA key authentication
# 1. Generate new SA key
gcloud iam service-accounts keys create staging-key.json \
  --iam-account=github-actions-staging@PROJECT.iam.gserviceaccount.com

# 2. Add key to GitHub Secrets
# Settings → Secrets → New: GCP_STAGING_SA_KEY

# 3. Revert workflow changes
git revert COMMIT_HASH
```

---

## Team Communication

### Phase 1 Announcement
**Subject**: Infrastructure Hardening Phase 1 - IAM and v2 Pilot

**Message**:
> We're starting production hardening this week. Phase 1 focuses on:
> - Removing public access from backend services
> - Narrowing IAM permissions
> - Piloting Cloud Run v2 migration
>
> **Impact**: None (changes in staging only)
> **Testing**: Please test staging after deployment
> **Questions**: Contact [lead]

### Phase 2 Announcement
**Subject**: Infrastructure Hardening Phase 2 - v2 Migration and VPC

**Message**:
> Phase 2 begins this week. Major changes:
> - All services migrating to Cloud Run v2
> - VPC networking being enabled
> - Secret volume mounts replacing env vars
>
> **Impact**: Potential service restarts during migration
> **Timeline**: 1-2 weeks, service-by-service rollout
> **Monitoring**: Watch for alerts during migration window
> **Questions**: Contact [lead]

### Production Launch Announcement
**Subject**: Production Infrastructure Hardened - Ready for Launch

**Message**:
> Production infrastructure hardening complete! 🎉
> - All services on Cloud Run v2
> - VPC networking active
> - Secrets via volume mounts
> - Monitoring and alerting configured
> - Workload Identity Federation enabled
>
> **Result**: Significantly improved security posture
> **Next Steps**: Production launch pending stakeholder approval
> **Documentation**: See docs/production-hardening-checklist.md

---

## Appendix: Quick Reference

### Commands
```bash
# Check service health
curl https://gateway-PROJECT.run.app/healthcheck

# View service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service" --limit=50

# Check IAM bindings
gcloud iam service-accounts get-iam-policy SA_EMAIL

# View autoscaling
gcloud run services describe SERVICENAME --region=us-east4 --format="value(metadata.annotations)"

# Tofu plan
cd infra && tofu plan -var-file=staging.auto.tfvars

# Tofu apply
cd infra && tofu apply -var-file=staging.auto.tfvars
```

### Key Files
- `docs/infra-production-audit.md` - Detailed gap analysis
- `docs/wif-setup.md` - Workload Identity Federation guide
- `docs/cloud-run-v2-migration.md` - v2 migration guide
- `docs/vpc-networking-strategy.md` - VPC design document
- `infra/main.tf` - Main infrastructure entry point
- `infra/networking.tf` - VPC resources (to be created)
- `.github/workflows/staging-deploy.yml` - Staging CI/CD
- `.github/workflows/production-deploy.yml` - Production CI/CD

### Support Contacts
- Infrastructure Lead: [Name]
- Security Lead: [Name]
- On-Call Rotation: [PagerDuty/Schedule]
