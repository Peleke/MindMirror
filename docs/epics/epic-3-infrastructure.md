# Epic 3: Production Infrastructure Hardening

**Epic ID:** EPIC-3
**Status:** Draft
**Priority:** P0 (Critical Path - Week 1-2, MUST complete before alpha invites)
**Estimated Effort:** 4-8 hours
**Story Points:** 15

---

## Epic Goal

Deploy secure, scalable production environment with Cloud Run v2 module, Supabase security improvements, bootstrapping automation, and environment separation - ensuring alpha user data never touches staging.

---

## Business Value

**Problem:** Alpha users will use production environment. Current staging uses Cloud Run v1 and shares Supabase with dev - not suitable for real user data or production security requirements.

**Solution:** Migrate to Cloud Run v2, create dedicated Supabase production project, implement one-command deployment with rollback capability.

**Impact:**
- Staging/production isolation prevents alpha user data contamination
- Cloud Run v2 enables min instances (no cold starts during alpha)
- Security hardening (RLS policies, 24h JWT expiry, Secret Manager) meets production standards
- One-command deployment reduces Week 2 production launch risk

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

### Story 3.1: Cloud Run v2 Migration
**File:** `docs/stories/3.1-cloud-run-v2-migration.md`
**Points:** 5
**Estimate:** ~2 hours

**As a** platform engineer
**I want** production deployment to use google_cloud_run_v2_service module
**So that** we leverage latest GCP features (min instances, startup CPU boost, better logging)

---

### Story 3.2: Supabase Separate Production Config
**File:** `docs/stories/3.2-supabase-production-config.md`
**Points:** 5
**Estimate:** ~2 hours

**As a** platform engineer
**I want** production environment to use dedicated Supabase project (not staging)
**So that** alpha user data is isolated and we can implement stricter security policies

---

### Story 3.3: Infrastructure Bootstrapping Automation
**File:** `docs/stories/3.3-infrastructure-bootstrapping.md`
**Points:** 3
**Estimate:** ~2 hours

**As a** platform engineer
**I want** one-command deployment that provisions all GCP + Supabase resources
**So that** disaster recovery or new environment setup takes minutes, not hours

---

### Story 3.4: Security Hardening
**File:** `docs/stories/3.4-security-hardening.md`
**Points:** 2
**Estimate:** ~1 hour

**As a** security-conscious engineer
**I want** production secrets managed via Secret Manager with least-privilege IAM
**So that** API keys and DB credentials aren't exposed in environment variables or logs

---

## Technical Assumptions

**Validated (from codebase inspection):**
- ✅ Current deployment uses `google_cloud_run_service` (v1) at `infra/modules/practices/main.tf:10`
- ✅ Module-based architecture for all services (`infra/main.tf`)
- ✅ Secrets managed via Google Secret Manager (partially implemented)
- ✅ 7 microservices + gateway to migrate (agent, journal, habits, meals, movements, practices, users)

**Dependencies:**
- Terraform (infrastructure-as-code)
- Supabase CLI for project bootstrapping
- GCP Secret Manager
- Alembic for database migrations

---

## Success Criteria

- [ ] Production deployment completes in <10 minutes (one command: `make production-deploy`)
- [ ] All 7 services + gateway use `google_cloud_run_v2_service` resource
- [ ] Dedicated Supabase production project with RLS policies enabled
- [ ] JWT expiry 24 hours (vs 7 days staging)
- [ ] Email confirmation required for signup
- [ ] Secrets accessed via volume mounts (not env vars)
- [ ] Service accounts have minimal IAM roles (practices_service → only practices DB access)
- [ ] Rollback mechanism works: `make production-rollback`
- [ ] Terraform plan shows clean migration (no unnecessary resource recreation)
- [ ] GCP billing <$100/month during alpha period

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cloud Run v2 migration breaks staging | Low | High | Test in isolated GCP project first; keep rollback Terraform state; run during low-traffic window |
| Supabase RLS policies misconfigured | Medium | Critical | Test voucher flow end-to-end before alpha invites; validate policy rules with SQL queries |
| Terraform state corruption during migration | Low | Critical | Backup state file before migration; use Terraform Cloud or GCS backend with versioning |
| Production costs exceed $100/month | Low | Low | Set GCP budget alerts at $75; monitor billing daily Week 1-2; scale down min instances if needed |
| Alembic migration fails in production | Low | High | Run migrations in staging first; validate schema changes; use blue/green or maintenance window |
| Secrets not properly mounted in Cloud Run v2 | Medium | High | Test secret access in staging v2 migration first; validate env vars available in container |

---

## Dependencies

**Blockers:**
- Epic 1 (Admin UI must exist before production deployment for alpha workflow)

**Blocks:**
- Week 2 Alpha User 1 invite (MUST deploy production by Day 3)
- Epic 4 production validation tests

**Parallel Work:**
- Can parallelize with Epic 2 (UI work independent of infra)
- Some overlap with Epic 4 (testing framework needs production env)

---

## Critical Path Notes

**TIMELINE CONSTRAINTS:**
- Week 1 (Days 1-5): Cloud Run v2 migration + Supabase setup
- Week 2 (Days 1-3): One-command deployment + security hardening
- **HARD DEADLINE:** Week 2 Day 3 (1 day buffer before Alpha User 1 invite Day 4)

**DEPLOYMENT STRATEGY:**
1. Test Cloud Run v2 in staging environment first
2. Create production Supabase project + RLS policies
3. Migrate Terraform to production with v2 resources
4. Validate full voucher flow end-to-end in production
5. Run Epic 4 manual test script before sending alpha invites

---

## Reference Materials

- **Cloud Run v2 Docs:** https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service
- **Current Infra:** `infra/main.tf`, `infra/modules/practices/main.tf`
- **Supabase CLI:** `supabase init`, `supabase db push`
- **Alembic Migrations:** `src/alembic-config/`, `habits_service/alembic/`, etc.

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-15 | v1.0 | Initial epic creation from PRD v4 | Sarah (PO Agent) |
