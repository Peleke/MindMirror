# Epic 10: UI Personalization Integration

**Epic ID:** EPIC-10
**Status:** Draft
**Priority:** P1 (Month 3 Feature - Post-Alpha Validation)
**Estimated Effort:** 6-10 hours
**Story Points:** 8

---

## Epic Goal

Connect extracted profiles to app UI for personalized experience - displaying calorie targets, macro splits, filtered workout programs, and incomplete profile notifications.

---

## Business Value

**Problem:** Even with profiles stored, the app still feels generic if UI doesn't adapt. Users won't see the value of completing onboarding if nothing changes.

**Solution:** Integrate profile data into meals dashboard (calorie targets), workout programs (filtering by preferences), and home screen (reminders for incomplete profiles).

**Impact:**
- Users see immediate value from completing onboarding (personalized calorie target)
- Workout programs feel curated to their goals (hide irrelevant programs)
- Incomplete profile reminders drive 20-30% increase in completion rate
- Foundation for future personalization (exercise substitutions, meal plans)

---

## Linked Requirements

- **FR7:** UI Personalization via Profiles
- **FR5:** Skip & Partial Profile Handling

---

## User Stories

### Story 10.1: Meals Dashboard Personalization
**File:** `docs/stories/10.1-meals-dashboard-personalization.md`
**Points:** 3
**Estimate:** ~2-3 hours

**As a** user
**I want** my daily calorie target displayed on meals dashboard
**So that** I know how much I should eat

---

### Story 10.2: Workout Program Filtering
**File:** `docs/stories/10.2-workout-program-filtering.md`
**Points:** 3
**Estimate:** ~2-3 hours

**As a** user
**I want** workout programs filtered by my training preferences
**So that** I only see relevant programs

---

### Story 10.3: Incomplete Profile Notifications
**File:** `docs/stories/10.3-incomplete-profile-notifications.md`
**Points:** 2
**Estimate:** ~2 hours

**As a** user
**I want** a reminder notification if I skip onboarding
**So that** I'm encouraged to complete my profile later

---

## Technical Assumptions

**Frontend Integration:**
- Meals dashboard: Fetch user profile via GraphQL `userProfile` query
- Workout programs: Filter based on `movement_profile.training_preferences`
- Notifications: Expo Notifications API for push reminders

**Validated:**
- ✅ GraphQL Hive Gateway federates users_service schema
- ✅ Mobile app uses Apollo Client for GraphQL queries
- ✅ Expo Notifications API supports scheduled push notifications

**Dependencies:**
- Epic 7 (requires `GET /users/{user_id}/profiles` API)
- Epic 9 (requires profiles to be created during onboarding)

---

## Success Criteria

- [ ] Meals dashboard displays personalized calorie target (if profile complete)
- [ ] Meals dashboard shows macro progress bar (protein/carbs/fat split)
- [ ] Workout programs filtered by training preference (strength users see strength programs)
- [ ] "Show all programs" toggle available for exploration
- [ ] Banner appears in home screen for incomplete profiles
- [ ] Push notification sent 24 hours after skip (one-time only)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Profile API latency delays UI load | Medium | Medium | Cache profile data locally; show skeleton loader while fetching |
| Filtering hides too many programs (user feels limited) | Medium | Low | Always show "Show all programs" toggle; start with loose filtering |
| Notification spam annoys users | Low | Medium | Send only once; allow disable in settings |

---

## Dependencies

**Blockers:**
- Epic 7 (requires profile storage + retrieval API)
- Epic 9 (requires onboarding conversation to create profiles)

**Blocks:**
- None (final epic in critical path)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-20 | v1.0 | Initial epic creation from Onboarding Agent PRD | Mary (Business Analyst) |
