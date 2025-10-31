# Sprint Summary - Alpha Validation Initiative

**Generated:** 2025-10-15
**Sprint Goal:** Create epics and stories for weekend implementation to prepare for alpha user onboarding
**PO Agent:** Sarah

---

## ✅ Completed

### Epic & Story Creation
- **4 Epics** created in `docs/epics/`
- **14 Stories** created in `docs/stories/`
- Epic 2 scope **REDUCED** from 8-14 hours to 6-8 hours (alpha-focused)

---

## 📋 Epic Summary

### Epic 1: Admin Tooling for Alpha Management
**Priority:** P0 (Critical Path - Week 1 Days 1-2)
**Effort:** 2-4 hours | **Story Points:** 6

**Stories:**
- ✅ 1.1: Magic Link Generation UI (3 pts, ~2 hrs)
- ✅ 1.2: Program Assignment Dashboard (2 pts, ~1.5 hrs)
- ✅ 1.3: Test User Account Management (1 pt, ~0.5-1 hr)

**Key Deliverable:** Web-based admin UI to onboard alpha users without SQL/CLI

---

### Epic 2: Workout UI/UX Overhaul (REDUCED SCOPE)
**Priority:** P1 (Week 1 Days 1-5, but lower than 1, 3, 4)
**Effort:** 6-8 hours (REDUCED from 8-14) | **Story Points:** 18 (REDUCED from 26)

**Stories:**
- ✅ 2.1: Exercise Card Redesign - Simplified (3 pts, ~2 hrs)
- ✅ 2.2: Set Table Complete Overhaul (8 pts, ~3 hrs) **CRITICAL PATH**
- ✅ 2.3: Rest Timer as Modal - Simplified (3 pts, ~1.5 hrs)
- ✅ 2.5: Minimal Visual Polish (4 pts, ~1 hr)

**DEFERRED:** Story 2.4 (Notes Input) - schema exists, UI implementation post-alpha

**Key Deliverable:** "Alpha-worthy" workout UI - functional and smooth, not pixel-perfect

---

### Epic 3: Production Infrastructure Hardening
**Priority:** P0 (Critical Path - Week 1-2, MUST complete before alpha invites)
**Effort:** 4-8 hours | **Story Points:** 15

**Stories:**
- ✅ 3.1: Cloud Run v2 Migration (5 pts, ~2 hrs)
- ✅ 3.2: Supabase Separate Production Config (5 pts, ~2 hrs)
- ✅ 3.3: Infrastructure Bootstrapping Automation (3 pts, ~2 hrs)
- ✅ 3.4: Security Hardening (2 pts, ~1 hr)

**Key Deliverable:** Production-ready environment with one-command deployment (`make production-deploy`)

---

### Epic 4: Alpha Testing Framework
**Priority:** P0 (Critical Path - Week 1 Day 3, before alpha invites)
**Effort:** 3-6 hours | **Story Points:** 12

**Stories:**
- ✅ 4.1: Voucher Flow Manual Test Script (3 pts, ~1.5 hrs)
- ✅ 4.2: Workout Execution Regression Tests - Foundation (8 pts, ~3-4 hrs)
- ✅ 4.3: Alpha Validation Checklist (1 pt, ~0.5 hrs)

**Key Deliverable:** Manual test scripts + E2E framework foundation to prevent P0 bugs

---

## 🎯 Recommended Implementation Order

**Priority Order:** Epics 1, 3, 4, 2 (per user request)
**Sequential Order:** 1 → 2 → 3 → 4 (treat sequentially)

### Week 1 Critical Path:
1. **Days 1-2:** Epic 1 (Admin Tooling) - Enables production onboarding workflow
2. **Days 1-5:** Epic 2 (Workout UI) - Parallel work, lower priority
3. **Day 3:** Epic 4 Story 4.1 (Manual Test Script) - Validation before alpha invites
4. **Days 3-5:** Epic 3 (Infrastructure) - Production deployment prep

### Week 2 Timeline:
- **Days 1-3:** Complete Epic 3 (production deployment) + Epic 4 (E2E tests)
- **Day 3:** HARD DEADLINE - Production deployed, ready for alpha
- **Day 4:** Alpha User 1 invite (after Epic 4 Story 4.1 manual test passes)

---

## 📊 Story Point Summary

| Epic | Stories | Story Points | Estimated Hours |
|------|---------|--------------|-----------------|
| Epic 1: Admin Tooling | 3 | 6 | 2-4 hours |
| Epic 2: Workout UI/UX | 4 | 18 | 6-8 hours |
| Epic 3: Infrastructure | 4 | 15 | 4-8 hours |
| Epic 4: Testing Framework | 3 | 12 | 3-6 hours |
| **TOTAL** | **14** | **51** | **15-26 hours** |

---

## ⚠️ Critical Blockers & Dependencies

### Epic 1 → Epic 3
- Admin UI (Epic 1) must complete before production deployment (Epic 3) for alpha workflow

### Epic 3 → Week 2 Alpha Invite
- Production deployment (Epic 3) MUST complete by Week 2 Day 3 (before Day 4 invite)

### Epic 4 → Alpha Invites
- Manual test script (Epic 4 Story 4.1) MUST pass before sending magic links

### Epic 2 Investigation Tasks (Day 1 Priority)
- **Story 2.2:** Verify GraphQL query for "previous workout" data (set table AC 2)
- **Story 2.2:** Test workout state persistence (backgrounding, navigation)

---

## 🚨 IMPORTANT NOTES

### Architecture Documentation Missing
- ❌ `docs/architecture/` directory does NOT exist
- ❌ `docs/architecture.md` file does NOT exist
- core-config.yaml expects sharded architecture at `docs/architecture/`
- **Recommendation:** Create architecture docs before or during implementation

### Epic 2 Scope Reduction
- **Original:** 8-14 hours, 26 story points, 5 stories
- **Reduced:** 6-8 hours, 18 story points, 4 stories
- **Rationale:** Rush to alpha onboarding - focus on functional improvements over aesthetics
- **Deferred:** Story 2.4 (Notes Input), advanced animations, deep design research

### Alpha Speed Focus
Each story has "ALPHA SPEED FOCUS" section identifying:
- What to cut if running over time
- Non-negotiable requirements
- Time caps to enforce scope discipline

---

## 📁 File Structure Created

```
docs/
├── epics/
│   ├── epic-1-admin-tooling.md
│   ├── epic-2-workout-ui-ux.md
│   ├── epic-3-infrastructure.md
│   └── epic-4-testing-framework.md
└── stories/
    ├── 1.1-magic-link-ui.md
    ├── 1.2-program-dashboard.md
    ├── 1.3-test-user-management.md
    ├── 2.1-exercise-card-redesign.md
    ├── 2.2-set-table-overhaul.md
    ├── 2.3-rest-timer-modal.md
    ├── 2.5-minimal-visual-polish.md
    ├── 3.1-cloud-run-v2-migration.md
    ├── 3.2-supabase-production-config.md
    ├── 3.3-infrastructure-bootstrapping.md
    ├── 3.4-security-hardening.md
    ├── 4.1-voucher-flow-test-script.md
    ├── 4.2-workout-regression-tests.md
    └── 4.3-alpha-validation-checklist.md
```

---

## ✅ Story Validation Checklist

All stories include:
- ✅ **Status:** Draft (ready for dev)
- ✅ **User Story Format:** "As a [role], I want [goal], so that [benefit]"
- ✅ **Acceptance Criteria:** Numbered, testable, unambiguous
- ✅ **Tasks/Subtasks:** Specific, actionable, references AC numbers
- ✅ **Dev Notes:** Source tree, technical details, implementation notes
- ✅ **Testing:** Test standards, frameworks, specific requirements
- ✅ **Change Log:** Initial creation tracked

**READY FOR DEV CYCLE** ✅

---

## 🚀 Next Steps

### For Product Manager (PM):
1. Review epics and stories for accuracy
2. Prioritize stories within each epic if needed
3. Create Google Sheets alpha validation checklist (Story 4.3)
4. Prepare to execute manual test script (Story 4.1) before alpha invites

### For Development Team:
1. Review Epic 1 stories (start with 1.1 Magic Link UI)
2. Investigate Day 1 blockers:
   - Story 2.2: Previous workout data GraphQL query
   - Story 2.2: Workout state persistence testing
3. Choose E2E framework (Story 4.2): Detox vs Maestro
4. Estimate sprint velocity (can all 14 stories fit in weekend?)

### For Platform Engineer:
1. Review Epic 3 stories
2. Backup Terraform state before any changes
3. Test Cloud Run v2 migration in staging first
4. Prepare production Supabase project setup

### For QA Engineer:
1. Review Epic 4 stories
2. Write voucher flow manual test script (Story 4.1)
3. Decide on E2E framework (Story 4.2)
4. Prepare test data and test accounts

---

## 📞 Questions & Clarifications

### Open Questions:
1. **Architecture docs:** Should we create `docs/architecture/` before implementation?
2. **E2E framework:** Detox (mature) or Maestro (faster setup)?
3. **Velocity:** Can all 14 stories (15-26 hours) fit in weekend? Need to prioritize?
4. **Previous workout data:** GraphQL query available or needs custom resolver?

### Risks:
- Epic 2 investigation tasks may reveal state management refactor needed (Story 2.2)
- Cloud Run v2 migration may break staging (mitigate: test in isolated project first)
- E2E test setup may exceed 4-hour estimate (mitigate: defer automated tests, use manual scripts)

---

## 🎉 Success Criteria for Weekend

**Green Light:**
- [ ] Epic 1 complete (admin UI functional)
- [ ] Epic 2 core stories complete (2.2 set table is critical)
- [ ] Epic 3 complete (production deployed)
- [ ] Epic 4 Story 4.1 complete (manual test script passes)

**Acceptable (Yellow Light):**
- [ ] Epic 1 + Epic 3 complete (can alpha onboard)
- [ ] Epic 2 partial (at least Story 2.2 set table done)
- [ ] Epic 4 Story 4.1 complete (manual testing validated)

**Red Light (Pivot):**
- [ ] Epic 1 or Epic 3 incomplete (cannot onboard alpha users)
- [ ] Manual test script (Story 4.1) reveals P0 bugs

---

**Ready to code! All stories validated and ready for dev cycle.** 🚀
