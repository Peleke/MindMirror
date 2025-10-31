# Epic 7: Profile Storage & Federation

**Epic ID:** EPIC-7
**Status:** Draft
**Priority:** P1 (Month 3 Feature - Post-Alpha Validation)
**Estimated Effort:** 8-12 hours
**Story Points:** 16

---

## Epic Goal

Create federated profile storage architecture with users_service as orchestrator and domain services (meals, movements) managing their profiles - enabling centralized profile retrieval and personalized UI experiences.

---

## Business Value

**Problem:** No structured storage for user preferences, goals, or physical attributes. UI cannot personalize calorie targets, macro recommendations, or program filtering without profile data.

**Solution:** Implement hub-and-spoke architecture where users_service orchestrates profile creation/retrieval across meals_service (eating profiles) and movements_service (movement profiles).

**Impact:**
- Enables UI personalization immediately after onboarding (calorie targets, macro splits)
- Supports future expansion to sleep/mindfulness profiles (clean domain separation)
- Single GraphQL API for frontend (no direct service-to-service calls from mobile)
- Scales cleanly as new verticals are added (meals, sleep, mindfulness)

---

## Linked Requirements

- **FR4:** Profile Extraction & Storage
- **FR7:** UI Personalization via Profiles

---

## User Stories

### Story 7.1: users_service GraphQL API Extensions
**File:** `docs/stories/7.1-users-service-graphql-api.md`
**Points:** 8
**Estimate:** ~4-5 hours

**As a** backend engineer
**I want** users_service to orchestrate profile creation/retrieval across services
**So that** frontend has single API for all profile operations

---

### Story 7.2: meals_service Eating Profile Storage
**File:** `docs/stories/7.2-meals-service-eating-profiles.md`
**Points:** 5
**Estimate:** ~3-4 hours

**As a** backend engineer
**I want** meals_service to store and serve eating profiles
**So that** eating preferences and calorie targets are managed in the appropriate domain service

---

### Story 7.3: movements_service Movement Profile Storage
**File:** `docs/stories/7.3-movements-service-movement-profiles.md`
**Points:** 3
**Estimate:** ~2-3 hours

**As a** backend engineer
**I want** movements_service to store training preferences and goals
**So that** workout programs can be filtered/recommended based on user profile

---

## Technical Assumptions

**Architecture Pattern:**
```
users_service (hub/orchestrator)
    ├─> meals_service DB (eating_profiles table)
    ├─> movements_service DB (movement_profiles table)
    └─> practices_service DB (habits_profiles table - future)
```

**Validated:**
- ✅ Separate databases per service (meals: port 5434, movements: port 5435)
- ✅ GraphQL Hive Gateway federates all service schemas
- ✅ Supabase auth provides user_id for row-level security

**Dependencies:**
- Alembic migrations for new tables
- GraphQL schema extensions in users_service
- REST endpoints in meals/movements services

---

## Success Criteria

- [ ] users_service GraphQL `createUserProfile` mutation works end-to-end
- [ ] Eating profile stored in meals_service DB with derived calorie target
- [ ] Movement profile stored in movements_service DB with training preferences
- [ ] `GET /users/{user_id}/profiles` returns aggregated data from all services
- [ ] Partial profiles supported (nulls for missing fields, no errors)

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cross-service orchestration latency (>500ms) | Medium | Medium | Use async/concurrent REST calls; cache profile data in users_service |
| Calorie calculation inaccurate (Harris-Benedict too generic) | Low | Low | Start simple; iterate based on user feedback; consider TDEE calculators post-MVP |
| Schema migration conflicts (multiple services) | Low | Medium | Coordinate Alembic migrations; test in staging first |

---

## Dependencies

**Blockers:**
- None (can start immediately, parallel to Epic 6)

**Blocks:**
- Epic 9 (Profile extraction requires storage endpoints)
- Epic 10 (UI personalization requires profile retrieval API)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-20 | v1.0 | Initial epic creation from Onboarding Agent PRD | Mary (Business Analyst) |
