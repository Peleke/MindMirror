# Epic 4: Alpha Testing Framework

**Epic ID:** EPIC-4
**Status:** Draft
**Priority:** P0 (Critical Path - Week 1 Day 3, before alpha invites)
**Estimated Effort:** 3-6 hours
**Story Points:** 12

---

## Epic Goal

Create reproducible manual test scripts, regression test suite foundation, and validation checklist for voucher-based auto-enrollment flow and workout execution - ensuring zero P0 bugs reach alpha users.

---

## Business Value

**Problem:** Manual testing is painful with no reproducible test scripts or validation checklist. Bugs require full re-test of voucher flow, wasting hours on rework.

**Solution:** Build "super ergonomic" manual test scripts that PM can execute, alpha validation checklist for tracking, and E2E test foundation for future automation.

**Impact:**
- Prevents embarrassing P0 bugs from reaching alpha users (critical for trust/retention)
- Reduces test execution time from 30+ minutes (manual exploration) to <10 minutes (scripted)
- Creates foundation for automated regression tests (defer implementation to Week 2-3)
- Provides clear tracking mechanism for alpha user progress and blockers

---

## Linked Requirements

- **FR10:** Alpha User Onboarding Validation
- **NFR7:** Testability (E2E tests run in CI/CD <5 minutes, test data isolated)
- **NFR8:** Observability (error tracking, user activity dashboard - Epic 5 overlap)

---

## User Stories

### Story 4.1: Voucher Flow Manual Test Script
**File:** `docs/stories/4.1-voucher-flow-test-script.md`
**Points:** 3
**Estimate:** ~1.5 hours

**As a** QA tester
**I want** step-by-step test script for voucher-based auto-enrollment flow
**So that** I can validate all 7 steps work correctly before inviting alpha users

---

### Story 4.2: Workout Execution Regression Tests (Foundation)
**File:** `docs/stories/4.2-workout-regression-tests.md`
**Points:** 8
**Estimate:** ~3-4 hours (framework setup + basic tests)

**As a** developer
**I want** automated UI tests for workout logging critical path
**So that** future UI changes don't break set logging, rest timer, or core functionality

**NOTE:** This story focuses on framework setup (Detox or Maestro) + basic smoke tests. Full test coverage deferred to Week 2-3.

---

### Story 4.3: Alpha Validation Checklist
**File:** `docs/stories/4.3-alpha-validation-checklist.md`
**Points:** 1
**Estimate:** ~0.5 hours

**As a** product manager
**I want** checklist tracking alpha user progress through onboarding + first 3 workouts
**So that** I know who's blocked and what features are causing friction

---

## Technical Assumptions

**Validated:**
- ✅ React Native Expo app (`mindmirror-mobile/`)
- ✅ Voucher flow documented (`docs/alpha-validation-week-1.md`)
- ✅ Week 1 execution checklist template exists (`docs/week-1-execution-checklist.md`)

**Requiring Investigation (Day 3 Priority):**
- ⚠️ **E2E framework choice** - Detox (mature, steeper learning curve) vs. Maestro (simpler, less flexible)
- ⚠️ **Test data seeding** - Need test Supabase accounts + test programs
- ⚠️ **CI/CD integration** - GitHub Actions vs. local pre-push hook

**Dependencies:**
- Admin UI (Epic 1) for magic link generation
- Production environment (Epic 3) for end-to-end validation
- Test Supabase accounts (can use Epic 1 Story 1.3 test account management)

---

## Success Criteria

- [ ] PM can execute manual test script in <30 minutes (including screenshots)
- [ ] Test script covers 7-step voucher flow + 3 edge cases (mismatched email, expired voucher, duplicate enrollment)
- [ ] E2E test framework setup complete (Detox or Maestro)
- [ ] Basic smoke tests pass: Load workout → Log set → Rest timer appears
- [ ] Alpha validation checklist pre-populated with 3 alpha users (knee rehab, AC dysfunction, combat athlete)
- [ ] Zero P0 bugs discovered after manual test script execution (run before every alpha invite)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| E2E test setup exceeds 4-hour estimate | Medium | Low | **Defer automated tests to Week 2-3**; rely on manual test scripts for Week 1 alpha invites; prioritize critical path coverage only |
| Voucher flow breaks after production deployment | Low | Critical | Run full manual test script (Story 4.1) in production before sending alpha invites |
| Manual test script too technical for PM | Low | Medium | Write for non-technical audience; include screenshots; validate PM can execute independently |
| Test data seeding complex | Medium | Low | Use Epic 1 Story 1.3 admin UI for test account creation; avoid custom SQL scripts |
| Edge cases not covered | Medium | Medium | Review with engineer + PM; prioritize scenarios from previous bug reports |

---

## Dependencies

**Blockers:**
- Epic 1 (Admin UI required for test execution)
- Epic 3 (Production environment required for production validation)

**Blocks:**
- Week 2 alpha invites (manual test script MUST pass before sending magic links)

**Parallel Work:**
- Can start Story 4.3 (checklist) immediately (no blockers)
- Story 4.1 requires Epic 1 completion
- Story 4.2 (E2E framework) can start in parallel but defer full implementation

---

## Testing Strategy

**Manual Testing (Week 1 Priority):**
1. Voucher flow 7-step script (Story 4.1)
2. Edge cases: Mismatched email, expired voucher, duplicate enrollment
3. Workout logging smoke test (manual, not automated yet)

**Automated Testing (Week 2-3 Deferred):**
1. E2E framework setup (Story 4.2 foundation)
2. Critical path tests: Load workout → Log sets → Rest timer → Complete workout
3. State persistence tests: Backgrounding, navigation, network interruption

**Alpha Validation Tracking:**
1. Google Sheets checklist (Story 4.3)
2. Weekly snapshots saved to `docs/testing/week-N-alpha-progress.md`

---

## E2E Framework Decision Matrix

| Framework | Pros | Cons | Recommendation |
|-----------|------|------|----------------|
| **Detox** | Mature, better debugging, more flexible | Steeper learning curve, 3-4hr setup | Recommended if team has RN E2E experience |
| **Maestro** | Simpler setup (~1hr), YAML-based tests | Less flexible, debugging harder | Recommended for alpha speed focus |

**Decision:** Defer to QA Engineer, but **lean Maestro for Week 1 speed** (can migrate to Detox post-alpha if needed).

---

## Reference Materials

- **Voucher Flow:** `docs/alpha-validation-week-1.md` (7-step breakdown)
- **Week 1 Checklist:** `docs/week-1-execution-checklist.md` (tracking template)
- **Mobile App:** `mindmirror-mobile/`
- **Detox Docs:** https://wix.github.io/Detox/
- **Maestro Docs:** https://maestro.mobile.dev/

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-15 | v1.0 | Initial epic creation from PRD v4 | Sarah (PO Agent) |
