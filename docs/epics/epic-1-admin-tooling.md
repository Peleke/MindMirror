# Epic 1: Admin Tooling for Alpha Management

**Epic ID:** EPIC-1
**Status:** Draft
**Priority:** P0 (Critical Path - Week 1 Days 1-2)
**Estimated Effort:** 2-4 hours
**Story Points:** 6

---

## Epic Goal

Streamline alpha user onboarding by providing admin UI for magic link generation, program creation/assignment, and user management - eliminating manual SQL queries and CLI friction.

---

## Business Value

**Problem:** Without admin tooling, manual SQL queries and CLI commands create operational bottlenecks for alpha user onboarding.

**Solution:** Build web-based admin UI extensions that enable non-technical PMs to onboard alpha users in minutes instead of hours.

**Impact:**
- Reduces alpha user onboarding time from 30+ minutes (SQL/CLI) to <5 minutes (UI form)
- Eliminates risk of SQL typos causing duplicate vouchers or incorrect program assignments
- Enables PM to independently manage alpha cohorts without engineering support

---

## Linked Requirements

- **FR1:** Magic Link Generation UI
- **FR2:** Program Assignment Dashboard
- **FR3:** Test User Account Management
- **FR10:** Alpha User Onboarding Validation

---

## User Stories

### Story 1.1: Magic Link Generation UI
**File:** `docs/stories/1.1-magic-link-ui.md`
**Points:** 3
**Estimate:** ~2 hours

**As a** coach/admin
**I want** a web form to generate magic links with embedded vouchers
**So that** I can onboard alpha users without writing SQL or using CLI tools

---

### Story 1.2: Program Assignment Dashboard
**File:** `docs/stories/1.2-program-dashboard.md`
**Points:** 2
**Estimate:** ~1.5 hours

**As a** coach/admin
**I want** a dashboard showing all created programs and their enrollments
**So that** I can verify alpha users are correctly assigned to workout programs

---

### Story 1.3: Test User Account Management
**File:** `docs/stories/1.3-test-user-management.md`
**Points:** 1
**Estimate:** ~0.5-1 hour

**As a** developer
**I want** admin UI to create test Supabase accounts with pre-assigned programs
**So that** I can reproduce alpha user scenarios without manual database manipulation

---

## Technical Assumptions

**Validated (from codebase inspection):**
- ✅ Admin panel exists at `web/src/app/admin`
- ✅ Voucher endpoints at `web/src/app/api/vouchers`
- ✅ Supabase Admin SDK available (`web/lib/supabase/admin.ts`)
- ✅ `autoEnrollPractices` mutation exists (tested by user)

**Dependencies:**
- Supabase authentication for admin role checks
- practices_service GraphQL endpoint for program/enrollment data
- Existing voucher creation logic (reuse/extend)

---

## Success Criteria

- [ ] PM can generate magic link in <1 minute via web form
- [ ] Dashboard shows real-time enrollment status for all programs
- [ ] Test accounts can be bulk-created (3-5 at once) with different programs
- [ ] Zero SQL queries required for alpha user onboarding workflow

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Admin role checks not implemented in Supabase | Low | Medium | Implement simple email allowlist check if RLS policies missing |
| Voucher creation endpoint edge cases | Medium | Medium | Test mismatched email, expired voucher, duplicate scenarios |
| UI doesn't work on mobile (PM field testing) | Low | Low | Use responsive design, test on phone before deployment |

---

## Dependencies

**Blockers:**
- None (can start immediately)

**Blocks:**
- Epic 3 (Production deployment requires admin UI for alpha invite workflow)
- Week 2 alpha user invites (must complete before sending magic links)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-15 | v1.0 | Initial epic creation from PRD v4 | Sarah (PO Agent) |
