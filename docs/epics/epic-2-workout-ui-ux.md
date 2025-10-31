# Epic 2: Workout UI/UX Overhaul (Alpha-Focused Scope)

**Epic ID:** EPIC-2
**Status:** Draft
**Priority:** P1 (Week 1 Days 1-5, but lower priority than Epic 1, 3, 4)
**Estimated Effort:** 6-8 hours (REDUCED from 8-14 hours)
**Story Points:** 18 (REDUCED from 26)

---

## Epic Goal

Transform workout execution interface to "alpha-worthy" quality by implementing **critical functional improvements only** - focusing on usability over aesthetics to enable meaningful user feedback during validation period.

**SCOPE REDUCTION RATIONALE:** We're rushing to alpha onboarding. Defer visual polish and non-critical features to post-validation. Focus: Make it work smoothly, not pixel-perfect.

---

## Business Value

**Problem:** Current UI is functional but alpha users need a smooth enough experience to provide meaningful feedback beyond "the UI is ugly."

**Solution:** Implement core UX improvements (set table clarity, rest timer prominence, exercise card readability) without deep design research or animation polish.

**Impact:**
- Alpha users can complete workouts without confusion (critical for 2+ workout success metric)
- Feedback focuses on program effectiveness rather than basic UI friction
- "Good enough for alpha" threshold met without over-investing in pre-validation polish

---

## Linked Requirements

- **FR4:** Exercise Card Redesign (simplified)
- **FR5:** Set Table Overhaul (core functionality)
- **FR6:** Rest Timer as Modal (critical UX pattern)
- **FR8:** Overall Visual Polish (REDUCED to essentials only)
- **FR9:** Workout State Persistence (assumed working, validate early)

**DEFERRED (Post-Alpha):**
- ~~FR7: Notes Input~~ (schema exists, defer UI implementation)
- ~~Deep design research (Behance/Hevy)~~ (use quick reference only)
- ~~Advanced animations~~ (spring physics, complex transitions)

---

## User Stories (Reduced Scope)

### Story 2.1: Exercise Card Redesign (Simplified)
**File:** `docs/stories/2.1-exercise-card-redesign.md`
**Points:** 3 (reduced from 5)
**Estimate:** ~2 hours (reduced from 2-3)

**As a** user
**I want** exercise cards to display name and target sets/reps prominently
**So that** I immediately understand what exercise to perform

**SCOPE CUT:** Defer GIF demos (use placeholders), skip accordion notes, minimal transitions

---

### Story 2.2: Set Table Complete Overhaul
**File:** `docs/stories/2.2-set-table-overhaul.md`
**Points:** 8 (unchanged - CRITICAL PATH)
**Estimate:** ~3 hours (reduced from 3-4)

**As a** user
**I want** a clean set table with clear previous/target/actual columns
**So that** logging sets feels effortless

**SCOPE MAINTAINED:** This is core functionality, must be solid for alpha

---

### Story 2.3: Rest Timer as Modal
**File:** `docs/stories/2.3-rest-timer-modal.md`
**Points:** 3 (reduced from 5)
**Estimate:** ~1.5 hours (reduced from 2)

**As a** user
**I want** rest timer to appear as a modal overlay
**So that** it's prominent and matches modern fitness app patterns

**SCOPE CUT:** Simplify design (circular progress optional), skip haptic refinement

---

### Story 2.5: Minimal Visual Polish (Alpha Essentials Only)
**File:** `docs/stories/2.5-minimal-visual-polish.md`
**Points:** 4 (reduced from 5)
**Estimate:** ~1 hour (reduced from 2-3)

**As a** user
**I want** workout screen to feel clean and professional
**So that** I'm not distracted by broken layouts or unreadable text

**SCOPE CUT:**
- No design tokens file (use inline styles)
- No skeleton screens (simple loading spinners)
- Basic spacing/typography only (skip animation library setup)

---

### ~~Story 2.4: Notes Input~~ (DEFERRED)
**Status:** DEFERRED to post-alpha validation
**Rationale:** Schema supports it (`practice_instance.notes` exists), but UI implementation non-critical for alpha. Users can provide notes via feedback form instead.

---

## Technical Assumptions

**Validated:**
- ✅ `practice_instance.notes` field exists (schema confirmed)
- ✅ React Native Expo setup (mindmirror-mobile/)
- ✅ Apollo Client for GraphQL

**Requiring Investigation (Day 1 Priority):**
- ⚠️ **Workout state persistence** - Test app backgrounding, navigation scenarios
- ⚠️ **Previous workout data query** - Verify GraphQL can fetch historical sets
- ⚠️ **GIF demo URLs** - Identify asset storage (or use placeholders)

**Dependencies:**
- Component location: `mindmirror-mobile/app/(app)/client/[id].tsx`
- practices_service GraphQL queries/mutations

---

## Success Criteria

- [ ] PM can complete full workout using new UI without confusion (dogfooding test)
- [ ] Set logging takes <10 seconds per set (including rest timer interaction)
- [ ] Zero visual regressions on iOS and Android
- [ ] No crashes during workout state persistence scenarios (backgrounding, navigation)

**Explicitly NOT Required for Alpha:**
- Perfect Hevy aesthetic match
- Advanced animations
- Dark mode support
- Notes input UI

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Workout state doesn't persist on navigation | Low | Critical | Investigate Day 1; may require state management refactor (Zustand) |
| Set table "previous" data not available | Medium | Medium | Use placeholder "—" if query complex; defer to post-alpha |
| Scope creep (team wants "pixel perfect") | High | Medium | **HARD STOP at 8 hours** - use time cap to enforce scope discipline |
| UI works on iOS but breaks on Android | Medium | High | Test on both platforms daily, prioritize iOS if time constrained |

---

## Dependencies

**Blockers:**
- None (can start immediately, parallel with Epic 1)

**Blocks:**
- None (Epic 1, 3, 4 are higher priority and don't depend on UI polish)

**Parallel Work:**
- Can work alongside Epic 1, 3, 4 (UI is independent)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-15 | v1.0 | Initial epic creation from PRD v4 | Sarah (PO Agent) |
| 2025-10-15 | v1.1 | SCOPE REDUCTION: 8-14hrs → 6-8hrs, deferred Story 2.4, simplified 2.1/2.3/2.5 | Sarah (PO Agent) |
