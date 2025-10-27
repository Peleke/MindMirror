# Epic 3: Production Infrastructure Hardening

**Epic ID:** EPIC-3
**Status:** Draft
**Priority:** P0 (Critical Path - 48hr alpha launch window)
**Estimated Effort:** 12-18 hours (Phase 1: 9-14hrs, Phase 2: 3-4hrs)
**Story Points:** 21

---

## Epic Goal

Deploy production-ready secure environment in **two phases**:
1. **Phase 1 (0-48hrs):** Manual deployment of hardened production infrastructure with VPC isolation, Cloud Run v2, dedicated Supabase, and gateway authentication - **BLOCKS alpha user onboarding**
2. **Phase 2 (48+ hrs):** Automated CI/CD pipeline for backend services - **CRITICAL for operational velocity post-launch**

---

## Business Value

**Problem:** Alpha users launching in 48 hours. Current staging environment is:
- Using Cloud Run v1 (misses performance features)
- **SECURITY RISK:** All mesh services publicly accessible (no VPC isolation)
- **SECURITY RISK:** Client can spoof `x-internal-id` header (no auth validation)
- Sharing Supabase with dev (not suitable for real user data)

**Solution (Two-Phase Approach):**

**Phase 1 - Secure Production Launch (BLOCKING):**
- Migrate to Cloud Run v2 (min instances, no cold starts)
- **VPC Connector + Private Mesh:** Gateway public, all mesh services private (ingress: internal)
- **Gateway Auth Enhancement:** JWT validation → users_service → internal ID (Redis-cached)
- Dedicated Supabase production project (RLS, 24h JWT, email confirmation)
- Secret Manager hardening (volume mounts, least-privilege IAM)
- Manual deployment via `make production-deploy` + documented runbook

**Phase 2 - CI/CD Automation (CRITICAL):**
- GitHub Actions pipeline for backend services
- Tag-triggered deployments (explicit control)
- Non-blocking test execution (tests run, failures don't block)
- Manual approval gate before production deployment

**Impact:**
- **Security:** VPC isolation prevents unauthorized mesh access; JWT validation eliminates spoofed IDs
- **Reliability:** Cloud Run v2 min instances eliminate cold starts during alpha
- **Velocity:** CI/CD enables rapid iteration post-launch without manual deployments
- **Compliance:** Staging/production isolation, Secret Manager, RLS policies meet security standards

---

## Linked Requirements

- **FR13:** Production Deployment with Cloud Run v2
- **NFR1:** Performance (2s load time, 200ms interactions, 500ms p95 GraphQL)
- **NFR2:** Reliability (99% uptime, zero data loss, graceful degradation)
- **NFR3:** Scalability (3→10 users without infra changes)
- **NFR4:** Security (JWT auth, RLS policies, Secret Manager, HTTPS only)
- **NFR6:** Maintainability (`make production-deploy` single command)
- **NFR11:** Supabase Bootstrapping Automation (idempotent setup)
- **NFR12:** Production Security Improvements (24h JWT, email confirmation, least-privilege IAM)

---

## User Stories

### **PHASE 1: ALPHA LAUNCH PREREQUISITES (0-48hrs) - BLOCKING**

---

### Story 3.1: Cloud Run v2 Migration
**File:** `docs/stories/3.1-cloud-run-v2-migration.md`
**Phase:** 1
**Points:** 3
**Estimate:** 1-2 hours

**As a** platform engineer
**I want** production deployment to use `google_cloud_run_v2_service` (OpenTofu)
**So that** we leverage min instances, startup CPU boost, and improved health checks

---

### Story 3.2: Supabase Production Bootstrapping
**File:** `docs/stories/3.2-supabase-production-config.md`
**Phase:** 1
**Points:** 3
**Estimate:** 2-3 hours

**As a** platform engineer
**I want** dedicated Supabase production project with documented setup process (manual + scripts)
**So that** alpha user data is isolated with RLS policies, 24h JWT expiry, and email confirmation

---

### Story 3.3: VPC Connector + Private Mesh Networking
**File:** `docs/stories/3.3-vpc-private-mesh.md`
**Phase:** 1
**Points:** 4
**Estimate:** 2-3 hours

**As a** security engineer
**I want** mesh services (users, agent, journal, etc.) accessible only via VPC (ingress: internal)
**So that** unauthorized public access is prevented; only gateway can reach mesh over VPC connector

---

### Story 3.4a: Gateway Authentication Enhancement (ID Exchange)
**File:** `docs/stories/3.4a-gateway-auth-id-exchange.md`
**Phase:** 1
**Points:** 5
**Estimate:** 3-4 hours

**As a** security engineer
**I want** gateway to parse JWT, query users_service for internal ID, cache result, and forward to mesh
**So that** clients cannot spoof `x-internal-id` (gateway becomes single auth validation point)

---

### Story 3.4b: Client x-internal-id Removal (Phased Cutover)
**File:** `docs/stories/3.4b-client-header-removal.md`
**Phase:** 1 (DEFERRED - after 3.4a proven stable)
**Points:** 1
**Estimate:** 30 mins

**As a** security engineer
**I want** to remove `x-internal-id` from client requests after 3.4a is validated
**So that** we complete the auth security hardening with zero client-side trust

---

### Story 3.5: Secret Manager Hardening
**File:** `docs/stories/3.5-secret-manager-hardening.md`
**Phase:** 1
**Points:** 2
**Estimate:** 1-2 hours

**As a** security engineer
**I want** all secrets (OPENAI_API_KEY, DATABASE_URL, Supabase keys) in Secret Manager with volume mounts
**So that** credentials aren't exposed in env vars or logs; least-privilege IAM enforced

---

### Story 3.7: Infrastructure Bootstrapping Automation
**File:** `docs/stories/3.7-infrastructure-bootstrapping.md`
**Phase:** 1
**Points:** 2
**Estimate:** 1-2 hours

**As a** platform engineer
**I want** `make production-deploy` command with synced runbook documentation
**So that** manual deployment is streamlined and repeatable for 48hr launch window

---

### **PHASE 2: CI/CD AUTOMATION (48+ hrs) - CRITICAL**

---

### Story 3.6: GitHub Actions CI/CD Pipeline
**File:** `docs/stories/3.6-cicd-pipeline.md`
**Phase:** 2
**Points:** 5
**Estimate:** 3-4 hours

**As a** platform engineer
**I want** tag-triggered GitHub Actions pipeline for backend services with non-blocking tests and manual approval
**So that** post-launch deployments are automated, safe, and don't require manual tofu apply

---

## Technical Assumptions

**Validated (from codebase inspection):**
- ✅ Current deployment uses `google_cloud_run_service` (v1) - need to migrate to v2
- ✅ Module-based OpenTofu architecture for all services
- ✅ Secrets partially in Secret Manager - need full migration
- ✅ 7 microservices + gateway: agent, journal, habits, meals, movements, practices, users
- ✅ Redis container available but unused (Celery deprecated) - perfect for gateway caching
- ✅ Gateway in `mesh/` (GraphQL Hive federation)
- ✅ Current auth: Client sends `x-internal-id` directly (INSECURE - no validation)

**Key Architectural Decisions:**
- **OpenTofu** (not Terraform) for infrastructure-as-code
- **VPC Networking:** Gateway + all mesh services in same VPC; VPC connector for Cloud Run inter-service communication
- **users_service** is CRITICAL path (entire system depends on it) - will eventually move to Kubernetes for HA, but Cloud Run for now
- **Redis** used exclusively for gateway ID caching (Supabase ID → internal ID mappings)
- **Phased cutover:** Implement gateway auth (3.4a) BEFORE removing client header (3.4b)

**Dependencies:**
- OpenTofu (infrastructure-as-code)
- Supabase CLI for project bootstrapping
- GCP Secret Manager
- Alembic for database migrations
- GitHub Actions (CI/CD Phase 2)

---

## Success Criteria

### **Phase 1 Success Criteria (BLOCKS alpha launch):**
- [ ] **Cloud Run v2:** All 7 services + gateway use `google_cloud_run_v2_service` resource (OpenTofu)
- [ ] **VPC Security:** Mesh services ingress set to `internal` (not publicly accessible)
- [ ] **VPC Connector:** Gateway can reach mesh services over VPC
- [ ] **Gateway Auth:** JWT parsed → users_service queried → internal ID cached (Redis) → forwarded to mesh
- [ ] **Gateway Auth Test:** Manual test proves client cannot spoof `x-internal-id` (gateway validation works)
- [ ] **Supabase Production:** Dedicated project created, RLS policies enabled, credentials in Secret Manager
- [ ] **Supabase Security:** JWT expiry 24 hours, email confirmation required
- [ ] **Secret Manager:** All secrets (OPENAI_API_KEY, DATABASE_URL, Supabase keys) volume-mounted (not env vars)
- [ ] **Least-Privilege IAM:** Each service has minimal IAM roles (e.g., practices_service → only practices DB access)
- [ ] **Deployment Command:** `make production-deploy` successfully deploys from runbook documentation
- [ ] **End-to-End Test:** Voucher flow works in production (signup → voucher → workout logging)
- [ ] **Cost Baseline:** GCP billing projected <$100/month during alpha period

### **Phase 2 Success Criteria (CRITICAL for velocity):**
- [ ] **GitHub Actions:** Pipeline triggers on git tag push
- [ ] **Path-based Builds:** Changes to `src/agent_service/` only build agent_service (isolated contexts)
- [ ] **Non-blocking Tests:** Unit + integration tests run, failures logged but don't block pipeline
- [ ] **Manual Approval:** Deployment requires manual approval gate after tests complete
- [ ] **Deployment Success:** Pipeline successfully deploys backend services to Cloud Run
- [ ] **Rollback:** Pipeline supports rollback to previous tag/deployment

---

## Risks & Mitigation

### **Phase 1 Risks:**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **VPC connector misconfiguration breaks gateway → mesh communication** | Medium | **CRITICAL** | Test VPC connectivity in staging first; validate each service reachable via internal URL; keep gateway public as fallback during testing |
| **Gateway auth logic bug allows spoofed IDs** | Medium | **CRITICAL** | Implement comprehensive manual testing: attempt to spoof `x-internal-id` with invalid JWT; validate Redis cache invalidation; add logging for all auth failures |
| **users_service downtime cascades to entire system** | Low | **CRITICAL** | Set min_instances=1 for users_service (no cold starts); monitor health checks closely; plan for Kubernetes migration post-alpha for HA |
| **Redis cache misconfiguration causes auth failures** | Medium | High | Test Redis connectivity before deployment; implement cache fallback (query users_service on cache miss); set reasonable TTL (e.g., 1 hour) |
| **Supabase RLS policies block legitimate users** | Medium | High | Test voucher flow end-to-end before alpha; validate RLS policy SQL queries manually; document emergency RLS disable procedure |
| **Cloud Run v2 migration causes service restart loops** | Low | High | Test v2 migration in staging first; configure startup probes with reasonable timeouts; keep rollback OpenTofu state |
| **Secret Manager volume mounts fail (services can't read secrets)** | Medium | **CRITICAL** | Test secret access in staging Cloud Run v2 services; validate IAM permissions for secret accessor role; add health check for secret availability |
| **48hr deadline missed due to scope creep** | High | High | **STRICT SCOPE CONTROL:** Defer Story 3.4b (client header removal) if needed; defer CI/CD (Story 3.6) to Phase 2; prioritize security (VPC, gateway auth) over nice-to-haves |

### **Phase 2 Risks:**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **CI/CD pipeline deploys broken code to production** | Medium | High | Require manual approval gate; run tests (non-blocking); use tag-based triggers (explicit control); implement rollback mechanism |
| **Path-based build isolation doesn't work (builds entire stack on small changes)** | Medium | Medium | Test path filters in GitHub Actions with dummy commits; document path patterns clearly; accept full build as fallback for now |
| **Brittle tests cause false negatives (pipeline always "fails" tests)** | High | Low | Make tests non-blocking; manual review decides if failures are acceptable; prioritize fixing tests post-alpha |

---

## Dependencies

**Blockers (Phase 1):**
- Epic 1 completion (Admin UI must exist for voucher workflow)
- OpenTofu infrastructure codebase exists and is working in staging

**Blocks (Phase 1):**
- Alpha user invite emails (HARD BLOCKER - cannot onboard users until Phase 1 complete)
- Epic 4 production validation tests (need production env to test)

**Blocks (Phase 2):**
- Developer velocity post-launch (manual deployments unsustainable for rapid iteration)

**Parallel Work:**
- Epic 2 (UI polish) can run parallel to Phase 1 infra work
- Phase 2 (CI/CD) can run parallel to Epic 4 (manual testing) after Phase 1 deploys

---

## Critical Path Notes

### **Phase 1: 48-Hour Launch Window (CRITICAL)**

**TIMELINE:**
- **Hour 0-4:** Story 3.1 (Cloud Run v2) + Story 3.2 (Supabase setup)
- **Hour 4-8:** Story 3.3 (VPC + Private Mesh) - TEST THOROUGHLY
- **Hour 8-12:** Story 3.4a (Gateway Auth) - HIGHEST RISK, MOST CRITICAL
- **Hour 12-14:** Story 3.5 (Secret Manager) + Story 3.7 (Bootstrapping automation)
- **Hour 14-18:** Manual testing, validation, fixes
- **HARD DEADLINE:** 48 hours from start

**DEPLOYMENT STRATEGY (Phase 1):**
1. **Test in staging FIRST:** Cloud Run v2 migration, VPC connector setup
2. **Create production Supabase:** Manual setup following documented runbook
3. **Deploy VPC + Private Mesh:** Gateway public, mesh services internal
4. **Deploy Gateway Auth:** Implement JWT → users_service → Redis cache flow
5. **Manual security testing:** Attempt to spoof `x-internal-id`, validate it fails
6. **End-to-end test:** Complete voucher flow (signup → magic link → workout log)
7. **Send alpha invites:** Users receive email while we work on Phase 2

### **Phase 2: Post-Launch Automation (CRITICAL)**

**TIMELINE:**
- **Start:** Immediately after Phase 1 deployment (while users sleep on email)
- **Duration:** 3-4 hours
- **Goal:** CI/CD pipeline operational before first user clicks signup link

**DEPLOYMENT STRATEGY (Phase 2):**
1. **Create GitHub Actions workflow:** Tag-triggered, path-based builds
2. **Configure test execution:** Non-blocking unit + integration tests
3. **Add manual approval gate:** Require human sign-off before production deployment
4. **Test pipeline:** Create test tag, validate pipeline runs successfully
5. **Document usage:** Tag creation → approval → deployment workflow

---

## Reference Materials

### **Infrastructure & Cloud**
- **OpenTofu Docs:** https://opentofu.org/docs/
- **Cloud Run v2:** https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service
- **VPC Connector:** https://cloud.google.com/vpc/docs/configure-serverless-vpc-access
- **Secret Manager:** https://cloud.google.com/secret-manager/docs
- **Current Infra Code:** `infra/main.tf`, `infra/modules/*/main.tf`

### **Supabase**
- **Supabase CLI:** https://supabase.com/docs/guides/cli
- **RLS Policies:** https://supabase.com/docs/guides/auth/row-level-security
- **Auth Config:** https://supabase.com/docs/guides/auth/auth-helpers

### **Gateway & Mesh**
- **Gateway Code:** `mesh/gateway.config.ts`, `mesh/mesh.config.ts`
- **GraphQL Hive:** https://the-guild.dev/graphql/hive
- **Redis Client (Node):** https://redis.io/docs/clients/nodejs/

### **CI/CD**
- **GitHub Actions:** https://docs.github.com/en/actions
- **Path Filters:** https://github.com/dorny/paths-filter

### **Database**
- **Alembic Migrations:** `src/alembic-config/`, `habits_service/alembic/`, etc.
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-15 | v1.0 | Initial epic creation from PRD v4 | Sarah (PO Agent) |
| 2025-10-18 | v2.0 | Complete rewrite with two-phase approach: Phase 1 (VPC security, gateway auth, Cloud Run v2, Supabase) + Phase 2 (CI/CD pipeline); expanded from 4 stories to 8 stories with detailed security hardening | Alex (DevOps Agent) |
