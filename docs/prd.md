# Product Requirements Document (PRD)
## Swae OS Soft Launch - Alpha Validation Initiative

**Document Version:** v4
**Last Updated:** 2025-10-15
**Product Manager:** John (PM Agent)
**Status:** Draft - Ready for Review

---

## Table of Contents

1. [Goals and Background Context](#1-goals-and-background-context)
2. [Requirements](#2-requirements)
3. [UI Design Goals](#3-ui-design-goals)
4. [Technical Assumptions](#4-technical-assumptions)
5. [Epic List](#5-epic-list)
6. [Epic Details with User Stories](#6-epic-details-with-user-stories)
7. [PM Checklist Execution](#7-pm-checklist-execution)
8. [Open Questions & Risks](#8-open-questions--risks)
9. [Next Steps & Handoff Prompts](#9-next-steps--handoff-prompts)

---

## 1. Goals and Background Context

### 1.1 Executive Summary

The Swae OS Soft Launch is a **4-week alpha validation initiative** designed to stress-test the voucher-based workout program infrastructure with 3 real users before investing in broader product development. This initiative focuses on **hardening existing functionality** (85% already built) rather than building new features, ensuring the core onboarding flow and workout execution experience are production-ready.

**Primary Goal:** Validate that the voucher-based auto-enrollment system works seamlessly for workout programs, achieving 2+ workouts per alpha user with zero P0 (critical) bugs.

**Timeline:** Week 1-4 (starting 2025-10-15)
- **Week 1:** Workout UI polish + Admin tooling + Production deployment prep
- **Week 2:** Production launch + Alpha User 1 invite (Day 4)
- **Week 3:** Alpha Users 2-3 invites (Days 6-7) + Bug fixes
- **Week 4:** Validation analysis + Decision point (green/yellow/red light for broader rollout)

### 1.2 Problem Statement

The current MindMirror system has 70-90% of the infrastructure required for workout program delivery (auto-enrollment mutations, practice instance tracking, GraphQL federation), but critical operational gaps prevent alpha user onboarding:

1. **No admin UI for magic link generation** - Requires manual SQL queries or CLI commands
2. **Workout execution UI lacks polish** - Functional but not "date-worthy" quality; alpha users will focus feedback on aesthetics rather than core functionality
3. **No production environment** - Staging uses Cloud Run v1 and shares Supabase with dev; not suitable for real user data
4. **Manual testing is painful** - No reproducible test scripts or validation checklist; bugs require full re-test of voucher flow

### 1.3 Target Users

Three alpha user segments (detailed in docs/alpha-validation-week-1.md):

1. **Knee Rehab Patient (Age 50+)**
   - **Context:** ACL reconstruction recovery, needs structured progression
   - **Program:** Conservative loading, tempo-controlled movements, ROM tracking
   - **Success criteria:** Completes 3 workouts without pain flare-ups, provides feedback on exercise clarity

2. **AC Dysfunction Desk Worker (Age 30-40)**
   - **Context:** Shoulder pain from poor ergonomics, needs corrective exercises
   - **Program:** Scapular stabilization, rotator cuff strengthening, posture drills
   - **Success criteria:** Completes 2 workouts, reports reduced pain, tests notes feature for pain tracking

3. **Combat Athlete (Age 25-35)**
   - **Context:** MMA/BJJ training, needs supplemental strength/conditioning
   - **Program:** Power development, isometric holds, injury prevention
   - **Success criteria:** Completes 4 workouts, stress-tests rest timer and set logging at high volume

### 1.4 Success Metrics

**Green Light (Proceed to broader validation):**
- All 3 alpha users complete 2+ workouts within first week
- Zero P0 bugs (app crashes, data loss)
- <2 P1 bugs (major UX friction) reported per user
- 50%+ workout adherence over 4-week period
- At least 1 alpha user volunteers enthusiastic testimonial

**Yellow Light (Iterate before scaling):**
- 2/3 alpha users complete 2+ workouts
- 1 P0 bug discovered but fixed within 24 hours
- 3-5 P1 bugs requiring UX improvements
- 30-50% workout adherence
- Mixed feedback (useful but needs polish)

**Red Light (Pivot or rebuild):**
- <2 alpha users complete even 1 workout
- Multiple P0 bugs or data integrity issues
- >5 P1 bugs indicating fundamental UX problems
- <30% workout adherence
- Negative feedback or user requests to stop testing

### 1.5 MVP Scope (In Scope for Alpha Validation)

**Core Functionality (85% Complete - Validation Focus):**
- ✅ Voucher-based auto-enrollment flow (7 steps: link generation → signup → program assignment)
- ✅ Workout program visibility in mobile app
- ⚠️ Workout execution UI (needs UX overhaul to match Hevy aesthetic)
- ⚠️ Set logging (weight, reps, completion tracking) - needs polish
- ⚠️ Rest timer - needs conversion from bottom sheet to modal
- ✅ GraphQL federation across 7 microservices
- ✅ Supabase authentication

**Operational Infrastructure (15% Complete - Build Focus):**
- ❌ Admin UI for magic link generation (currently manual CLI)
- ❌ Production environment with Cloud Run v2 (currently staging only)
- ❌ Manual test scripts for voucher flow validation
- ❌ Error tracking and user activity monitoring

**New Features (Deferred):**
- Notes input for sets/exercises (schema supports it, UI doesn't expose it yet)
- Exercise GIF demos (nice-to-have, use placeholder thumbnails for alpha)
- Workout history view (data persists, just not visualized yet)
- Progress charts (deferred to Month 3 validation mode)

### 1.6 Out of Scope (Post-Alpha Validation)

**Month 3 Features (250 users):**
- AI weekly summaries (RAG across journal/habits/meals/workouts)
- Onboarding interview bot (chat-native structured profiling)
- CV-based meal logging (photo → composition analysis)
- Stripe-gated marketplace (subscription unlocks all programs)

**Month 6 Features (Competitive Differentiation):**
- Multi-agent adaptive planning system (specialized nutritionist/coach/behavior agents)
- Graph database migration (Postgres → MemGraph/Neo4j)
- Ambient agent triggers (environment-based interventions)
- Deep research agents analyzing holistic data (meals, workouts, journal, sleep, menstrual cycles)

**Infrastructure Improvements (Post-Validation):**
- GitOps CI/CD (Weeks 5-7, not Week 1 blocker)
- Agent service refactor (LangGraph + FastAPI template merge)
- Celery/Redis removal (migrate to GCP Pub/Sub)
- Qdrant vector DB usage (not required for workout programs)

---

## 2. Requirements

### 2.1 Functional Requirements

**FR1: Magic Link Generation UI**
Admin web interface shall provide a form to generate magic links with embedded vouchers for workout program assignment.

**Acceptance Criteria:**
- Form accepts email, program_id, optional expiration date
- Validates email format and program existence before submission
- Returns copyable magic link + voucher ID on success
- Shows clear error messages for invalid inputs
- Only accessible to authenticated admin users (Supabase role check)

---

**FR2: Program Assignment Dashboard**
Admin dashboard shall display all workout programs and their enrollment status.

**Acceptance Criteria:**
- Lists programs with name, creation date, enrolled user count
- Drill-down to see enrolled users per program (email, enrollment date, completion %)
- Visual indicators for active vs. completed enrollments
- Search/filter by program name or user email

---

**FR3: Test User Account Management**
Admin UI shall enable creation of test Supabase accounts with pre-assigned programs.

**Acceptance Criteria:**
- Form accepts email, password, program_id
- Creates Supabase user + auto-generates voucher + triggers enrollment flow
- Returns login credentials for immediate testing
- Supports bulk creation (3-5 test accounts)

---

**FR4: Exercise Card Redesign**
Workout screen shall display exercise cards with prominent name, GIF demo, and target sets/reps.

**Acceptance Criteria:**
- Layout: Exercise name (24px bold) at top, GIF thumbnail (120px square) centered, target sets/reps below
- Tapping GIF → full-screen demo view with swipe-to-dismiss
- Exercise notes (if present) in collapsed accordion
- Matches Hevy's card visual hierarchy
- Smooth transitions (200ms ease-in-out)

---

**FR5: Set Table Overhaul**
Set logging interface shall display clean, minimalist table with previous/target/actual columns.

**Acceptance Criteria:**
- Columns: Set # | Previous | Target | Weight | Reps | ✓ (completion)
- Previous column shows greyed-out historical data (read-only)
- Target column shows prescribed sets/reps (read-only)
- Weight/Reps have numeric inputs with +/- stepper buttons
- Completion checkbox fills row with success color (green tint)
- Auto-advance focus: Weight → Reps → Next set weight
- Matches Hevy's table density and spacing

---

**FR6: Rest Timer as Modal**
Rest timer shall appear as prominent modal overlay (not bottom sheet).

**Acceptance Criteria:**
- Triggers automatically after completing a set (checkbox checked)
- Modal centered with circular progress ring, countdown (90s default), Skip/Add 30s buttons
- Background dimmed (80% opacity black overlay)
- Tapping outside modal does NOT dismiss
- Haptic feedback at 10s, 5s, 0s remaining
- Matches Hevy's rest timer aesthetic

---

**FR7: Notes Input for Sets/Exercises**
User shall be able to add notes about pain, form adjustments, or PRs after each set or exercise.

**Acceptance Criteria:**
- Notes icon button at set row level and exercise card level
- Tapping icon → text input modal (200 char limit, Save/Cancel buttons)
- Saved notes appear as collapsed text with expand icon
- Notes persist to practice_instance.notes field
- Notes visible in workout history view (future feature, just ensure data saves)

---

**FR8: Overall Visual Polish**
Workout screen shall feel modern, professional, and motivating (matching Hevy aesthetic).

**Acceptance Criteria:**
- Typography: System font stack (SF on iOS, Roboto on Android), consistent sizing
- Color palette: Primary blue (#4A90E2), success green (#7ED321), neutral grays
- Spacing: 16px padding standard, 8px related elements, 24px sections
- Shadows: Subtle elevation (2dp, 0.1 opacity)
- Animations: Fade-in for exercises, slide-up for modals, spring physics for interactions
- Loading states: Skeleton screens (no blank white screens)

---

**FR9: Workout State Persistence**
User's workout progress (duration, sets logged) shall persist when navigating away from workout screen.

**Acceptance Criteria:**
- User logs 2 sets → navigates to home → returns to workout → sees 2 sets still logged
- Duration timer continues running in background (or saves elapsed time)
- No data loss on app backgrounding or network interruption
- Optimistic UI updates (immediate feedback, sync when network available)

---

**FR10: Alpha User Onboarding Validation**
System shall support end-to-end alpha user onboarding flow with manual validation checklist.

**Acceptance Criteria:**
- Manual test script covers 7-step voucher flow (link generation → signup → workout completion)
- Edge cases tested: Mismatched email, expired voucher, duplicate enrollment
- Test script executable by non-technical PM (clear instructions, screenshots)
- Alpha validation checklist tracks: Signup date, workouts completed, bugs reported

---

**FR11: Error Tracking for Alpha Support**
Mobile app shall automatically report errors to centralized logging system.

**Acceptance Criteria:**
- Unhandled exceptions, GraphQL failures, network timeouts captured
- Error reports include: User ID, device info, breadcrumbs (last 10 actions), stack trace
- Alert threshold: >3 errors from same user within 1 hour → notification
- Privacy: No PII logged (exclude email, names)

---

**FR12: User Activity Monitoring Dashboard**
Admin dashboard shall display alpha user engagement metrics in real-time.

**Acceptance Criteria:**
- Per-user metrics: Last login, workouts completed, completion rate, session duration
- Feature usage tracking: Notes added, rest timer used
- Real-time updates (5-minute refresh)
- Filter by user or date range
- Export to CSV

---

**FR13: Production Deployment with Cloud Run v2**
Production environment shall use google_cloud_run_v2_service module for all microservices.

**Acceptance Criteria:**
- All 7 services (agent, journal, habits, meals, movements, practices, users) + gateway use v2
- Environment variables and secrets configuration equivalent to staging
- Health checks with proper startup/liveness probes
- Min instances set to 1 for practices_service (prevent cold starts)
- Terraform plan shows clean migration (no unnecessary resource recreation)

---

### 2.2 Non-Functional Requirements

**NFR1: Performance**
- Workout screen loads within 2 seconds on 4G network
- Set logging interactions respond within 200ms (optimistic UI updates)
- GraphQL queries complete within 500ms (p95)

**NFR2: Reliability**
- 99% uptime for production environment during alpha period
- Zero data loss for logged workouts (even if app crashes)
- Graceful degradation if backend services unavailable (offline mode)

**NFR3: Scalability**
- System supports 3 concurrent alpha users (Day 1) → 10 users (Day 30) without infrastructure changes
- Database connection pooling handles 50 concurrent requests
- Cloud Run autoscaling: 1 min instance → 5 max instances

**NFR4: Security**
- All API requests authenticated via Supabase JWT
- Row-level security (RLS) enabled on vouchers table
- Secrets managed via Google Secret Manager (no .env files in production)
- HTTPS only for all client-server communication

**NFR5: Usability**
- New alpha user completes first workout within 10 minutes of signup (no onboarding tutorial required)
- Set logging interaction follows Hevy's UX patterns (familiar to fitness app users)
- Accessibility: Minimum 44px touch targets, WCAG AA color contrast

**NFR6: Maintainability**
- Test scripts executable by non-engineer (PM can validate voucher flow)
- Infrastructure deployed via single `make production-deploy` command
- All configuration managed via Terraform (no manual ClickOps)

**NFR7: Testability**
- E2E tests run in CI/CD within 5 minutes
- Test data isolated from production (dedicated test Supabase accounts)
- Manual test script covers critical path + edge cases

**NFR8: Observability**
- Error tracking captures unhandled exceptions with context (user ID, device info, breadcrumbs)
- User activity dashboard shows real-time engagement metrics
- Cloud Run logs centralized in GCP Logging with 30-day retention

**NFR9: Cost Efficiency**
- Production infrastructure costs <$100/month for alpha (3 users, low traffic)
- Cloud Run scales to zero when idle (non-critical services)
- Supabase free tier sufficient for alpha period

**NFR10: Developer Experience**
- Local development environment starts with `make demo` (single command)
- Infrastructure changes tested in staging before production
- Rollback mechanism via `make production-rollback`

**NFR11: Supabase Bootstrapping Automation**
- One-command setup provisions Supabase project with RLS policies and auth configuration
- Idempotent: Running setup twice doesn't break existing resources
- Script validates prerequisites (Supabase CLI, gcloud auth)

**NFR12: Production Security Improvements**
- JWT expiry reduced to 24 hours (vs 7 days in staging)
- Email confirmation required for signup (prevent typo-based account hijacking)
- Service accounts use least-privilege IAM roles (practices_service → only practices DB access)

---

## 3. UI Design Goals

### 3.1 Design Philosophy

The workout execution interface must achieve **"date-worthy" quality** - polished enough that users are excited to show friends, not embarrassed by amateur aesthetics. We're explicitly **cloning Hevy's design language** to leverage proven UX patterns familiar to fitness app users.

**Design Principles:**
1. **Clarity over cleverness** - Exercise name and target sets/reps immediately visible, no hunting for info
2. **Minimize cognitive load** - Previous workout data shown for context, but greyed out to distinguish from current session
3. **Immediate feedback** - Optimistic UI updates, haptic feedback, visual confirmation for logged sets
4. **Familiar interactions** - If Hevy users expect a modal rest timer, we use a modal (not a bottom sheet)

### 3.2 Component-Level Design Requirements

**Exercise Cards:**
- Large, bold exercise name (24px, system font weight 700)
- GIF thumbnail centered (120px square, rounded corners 8px)
- Target sets/reps below GIF in secondary text (16px, weight 400)
- Collapsed accordion for exercise notes (if present)
- Card elevation: 2dp shadow, white background
- Spacing: 16px padding, 24px margin between cards

**Set Table:**
- Clean, minimalist table layout (no heavy borders, subtle dividers)
- Column headers: Set # | Previous | Target | Weight | Reps | ✓
- Previous/Target columns read-only, greyed out (#9E9E9E)
- Weight/Reps inputs with +/- stepper buttons (larger touch targets, 44px min)
- Completion checkbox fills row with success tint (#E8F5E9, Material Green 50)
- Auto-advance focus for keyboard flow (Weight → Reps → Next set)
- Density: Compact but not cramped (Hevy's 12px row padding)

**Rest Timer Modal:**
- Centered overlay (80% screen width, auto height)
- Circular progress ring (120px diameter, 8px stroke width)
- Countdown text inside ring (48px bold, primary color)
- Action buttons below: Skip (secondary style) | Add 30s (tertiary style)
- Background dimmed overlay (rgba(0, 0, 0, 0.8))
- Haptic feedback: Medium impact at 10s, 5s; Heavy impact at 0s
- Spring animation for modal appearance (react-native-reanimated)

**Notes Input:**
- Icon button: Note outline icon (24px, positioned at set row end or exercise card footer)
- Modal: Full-screen on small devices, 60% width on tablets
- Text input: Multiline, 200 char limit, character counter visible
- Placeholder: "Add note (e.g., pain level, form adjustment, PR)"
- Buttons: Cancel (secondary) | Save (primary, disabled if empty)

**Overall Visual System:**
- **Typography:** SF Pro (iOS), Roboto (Android), fallback system fonts
- **Color Palette:**
  - Primary: #4A90E2 (blue, action buttons)
  - Success: #7ED321 (green, completed sets)
  - Error: #D0021B (red, validation errors)
  - Neutrals: #212121 (text primary), #757575 (text secondary), #F5F5F5 (background)
- **Spacing Scale:** 4px, 8px, 12px, 16px, 24px, 32px (multiples of 4)
- **Shadows:** 2dp elevation for cards, 8dp for modals (Material Design standard)
- **Animations:**
  - Fade-in: 200ms ease-in-out
  - Slide-up: 300ms spring (damping 0.8, stiffness 100)
  - Button press: 100ms scale (0.95) with haptic

### 3.3 Design Reference Materials

**Primary Inspiration:**
- Hevy workout app (search "Hevy UI" on Behance/Dribbble for screenshots)
- Material Design 3 components (for Android baseline)
- Apple Human Interface Guidelines (for iOS baseline)

**Design System Libraries (Recommended):**
- NativeBase (React Native component library, pre-built accessible components)
- Tamagui (performance-optimized, style system similar to Tailwind)
- React Native Paper (Material Design implementation)

**Time Budget:**
- Design research (Behance, Hevy screenshots): 1-2 hours
- Design tokens file setup: 1 hour
- Component implementation: 6-10 hours
- Testing + refinement: 1-2 hours
- **Total:** 8-14 hours

### 3.4 Accessibility Requirements

**WCAG AA Compliance:**
- Color contrast ratio ≥4.5:1 for text, ≥3:1 for UI components
- Touch targets ≥44px (iOS) / ≥48px (Android)
- Screen reader labels for all interactive elements
- Focus indicators visible for keyboard navigation (future tablet support)

**Inclusive Design:**
- Support for system font scaling (respect user's text size preferences)
- Haptic feedback benefits users with visual impairments (non-visual confirmation)
- Notes input supports voice-to-text (default platform behavior)

---

## 4. Technical Assumptions

### 4.1 Validated Assumptions (Confirmed via Codebase Inspection)

**✅ Schema & Data Model:**
- `practice_instance.notes` field exists (practices_service/practices/repository/models/practice_instance.py:37)
  ```python
  notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  ```
- `duration`, `completed_at`, `date` fields support workout state persistence
- Historical practice_instance data queryable for "previous workout" comparison

**✅ GraphQL Mutations:**
- `autoEnrollPractices` mutation exists (enrollment_resolvers.py:330) - user has tested successfully
- `defer_practice` mutation supports 'push' and 'shift' modes (enrollment_resolvers.py:926)
- Habits service auto-enrollment integration present (lines 534-586)

**✅ Infrastructure:**
- Current deployment uses `google_cloud_run_service` (infra/modules/practices/main.tf:10) - NOT v2
- Module-based architecture for all services (infra/main.tf)
- Secrets managed via Google Secret Manager
- Admin panel exists at web/src/app/admin
- Voucher endpoints at web/src/app/api/vouchers

**✅ Authentication & Authorization:**
- Supabase Auth handles user authentication (no custom JWT logic needed)
- Magic links generated by web subdirectory voucher endpoint
- Email rendering via React + Supabase Edge Functions (web/supabase/edge-functions/)
- Admin UI accessible via Supabase role-based checks

**✅ Database Architecture:**
- PostgreSQL practices DB on port 5436 (separate from main DB on 5432)
- GraphQL Hive Gateway federates all 7 service schemas
- No Celery/Redis for alpha - using fire-and-forget sync calls
- Future migration to GCP Pub/Sub deferred post-validation

### 4.2 Assumptions Requiring Investigation

**⚠️ Workout State Persistence:**
- **Assumption:** Duration timer + logged sets persist when user navigates away from workout screen
- **Investigation needed:** Test app backgrounding, navigation to other screens, network interruption scenarios
- **Risk:** If state doesn't persist, may require state management refactor (Zustand/Redux)
- **Timeline:** Investigate Day 1 (critical for alpha UX)

**⚠️ Notes Field Scope:**
- **Assumption:** practice_instance.notes supports both exercise-level and set-level notes
- **Investigation needed:** Verify GraphQL mutation accepts notes parameter, check if UI needs set-level granularity
- **Risk:** May need schema extension if current notes field is exercise-only
- **Timeline:** Investigate Day 1 (before implementing FR7)

**⚠️ "Previous Workout" Data Retrieval:**
- **Assumption:** practices_service stores historical practice_instance data for set table "Previous" column
- **Investigation needed:** Verify GraphQL query can fetch last workout's sets for same exercise
- **Risk:** If historical data not readily accessible, may need custom query or denormalization
- **Timeline:** Investigate Day 2 (before implementing FR5 set table overhaul)

### 4.3 Technology Stack Assumptions

**Frontend (Mobile App):**
- React Native with Expo (confirmed in mindmirror-mobile/)
- TypeScript with fp-ts for functional programming patterns
- Apollo Client for GraphQL communication
- Supabase Auth SDK for authentication
- React Native Reanimated for animations (or fallback to Animated API)

**Backend (Microservices):**
- FastAPI (Python) for all 7 services
- PostgreSQL with SQLAlchemy async
- GraphQL federation via Hive Gateway
- Alembic for database migrations

**Infrastructure:**
- GCP Cloud Run for service deployment
- Google Secret Manager for secrets
- Supabase for auth + voucher storage
- Terraform for infrastructure-as-code

**Testing:**
- Detox or Maestro for React Native E2E tests (decision deferred to QA engineer)
- Manual test scripts for alpha validation
- GCP Error Reporting for error tracking (simpler than Sentry for alpha)

### 4.4 Dependency Assumptions

**External Dependencies:**
- Supabase free tier sufficient for alpha (3 users, low traffic) ✅
- GCP Cloud Run free tier sufficient for alpha (<$100/month) ✅
- OpenAI API not required for alpha (workout programs don't use LLM) ✅

**Internal Dependencies:**
- Voucher flow (FR1-3) must complete before alpha invites sent (Week 1 blocker)
- Production deployment (FR13) must complete before alpha user data enters system (Week 2 blocker)
- Workout UI polish (FR4-8) should complete before alpha invites for best first impression (Week 1 priority, not hard blocker)

**Timeline Dependencies:**
- Admin tooling (Epic 1) → Enables production deployment prep (Epic 3)
- Production deployment (Epic 3) → Enables Alpha User 1 invite (Week 2 Day 4)
- Testing framework (Epic 4) → Enables confident alpha invites (reduces risk of embarrassing bugs)

---

## 5. Epic List

### Epic 1: Admin Tooling for Alpha Management
**Description:** Build admin UI extensions to streamline magic link generation, program creation/assignment, and user management for alpha testing workflow.

**Linked Requirements:** FR1, FR2, FR3, FR10

**Rationale:** Without admin tooling, manual SQL queries and CLI commands create friction for alpha user onboarding. This epic eliminates operational bottlenecks.

**Estimated Effort:** 2-4 hours

---

### Epic 2: Workout UI/UX Overhaul
**Description:** Transform workout execution interface to "date-worthy" quality by cloning Hevy's aesthetic - redesigned set table, modal rest timer, notes input, and overall visual polish.

**Linked Requirements:** FR4, FR5, FR6, FR7, FR8, FR9

**Rationale:** Current UI is functional but not user-delightful. Alpha users need a smooth experience to provide meaningful feedback beyond "the UI is ugly."

**Estimated Effort:** 8-14 hours (includes Behance/design research)

---

### Epic 3: Production Infrastructure Hardening
**Description:** Deploy production environment with Cloud Run v2 module, Supabase security improvements, bootstrapping automation, and environment separation.

**Linked Requirements:** FR13, NFR1, NFR2, NFR3, NFR4, NFR5, NFR6, NFR11, NFR12

**Rationale:** Alpha users will use production environment. Staging/production parity and security hardening are table stakes before real user data enters the system.

**Estimated Effort:** 4-8 hours (infrastructure-as-code changes)

---

### Epic 4: Alpha Testing Framework
**Description:** Create reproducible manual test scripts, regression test suite, and validation checklist for voucher-based auto-enrollment flow and workout execution.

**Linked Requirements:** NFR7, NFR8, NFR9

**Rationale:** "Super ergonomic way to run these tests" ensures bugs caught in alpha don't regress later and tests can eventually be automated.

**Estimated Effort:** 3-6 hours

---

### Epic 5: Alpha Monitoring & Support
**Description:** Implement error tracking, user activity monitoring, and bug triage process to support alpha users in real-time during Week 1-4 validation period.

**Linked Requirements:** NFR10, FR11, FR12

**Rationale:** Alpha users will hit bugs. We need visibility into failures and fast response time to maintain trust and get quality feedback.

**Estimated Effort:** 2-4 hours

---

**Total Estimated Effort:** 19-36 hours across 4 weeks

**Critical Path:** Epic 1 → Epic 2 → Epic 3 → Epic 4 (Epic 5 can run in parallel with Epic 4)

**Week 1 Priorities:** Epic 1 (Days 1-2), Epic 2 (Days 1-5), Epic 4 subset (Day 3)

**Week 2-3 Priorities:** Epic 3 (production deployment), Epic 4 completion, Epic 5 setup

**Week 4:** Buffer for alpha user support and bug fixes

---

## 6. Epic Details with User Stories

### Epic 1: Admin Tooling for Alpha Management

**Epic Goal:** Streamline alpha user onboarding by providing admin UI for magic link generation, program creation/assignment, and user management.

---

#### Story 1.1: Magic Link Generation UI
**As a** coach/admin
**I want** a web form to generate magic links with embedded vouchers
**So that** I can onboard alpha users without writing SQL or using CLI tools

**Acceptance Criteria:**
- Admin UI at `/admin/vouchers/create` accepts: email, program_id, expiration date
- Form validates email format and program existence before submission
- Success response displays copyable magic link + voucher ID
- Error states show clear messages (invalid program, duplicate voucher, etc.)
- UI only accessible to authenticated admin users (Supabase role check)

**Implementation Notes:**
- Extend existing web/src/app/admin structure
- Reuse voucher creation endpoint at web/src/app/api/vouchers
- ~2 hours estimated

**Story Points:** 3

---

#### Story 1.2: Program Assignment Dashboard
**As a** coach/admin
**I want** a dashboard showing all created programs and their enrollments
**So that** I can verify alpha users are correctly assigned to workout programs

**Acceptance Criteria:**
- Dashboard lists all programs with: name, creation date, enrolled user count
- Click program → shows enrolled users with: email, enrollment date, completion status
- Visual indicator for "active" vs "completed" enrollments
- Search/filter by program name or user email
- Responsive design (works on mobile for field testing)

**Implementation Notes:**
- Query practices_service GraphQL endpoint for program + enrollment data
- ~1.5 hours estimated

**Story Points:** 2

---

#### Story 1.3: Test User Account Management
**As a** developer
**I want** admin UI to create test Supabase accounts with pre-assigned programs
**So that** I can reproduce alpha user scenarios without manual database manipulation

**Acceptance Criteria:**
- Form accepts: email, password, program_id
- Creates Supabase user account via Admin SDK
- Auto-generates voucher and triggers auto-enrollment flow
- Returns login credentials for immediate testing
- Option to bulk create 3-5 test accounts with different programs

**Implementation Notes:**
- Use Supabase Admin SDK (web/lib/supabase/admin.ts)
- ~0.5-1 hour estimated

**Story Points:** 1

---

### Epic 2: Workout UI/UX Overhaul

**Epic Goal:** Transform workout execution interface to "date-worthy" quality by cloning Hevy's aesthetic and fixing UX friction points.

---

#### Story 2.1: Exercise Card Redesign
**As a** user
**I want** exercise cards to display name, target sets/reps, and GIF demo prominently
**So that** I immediately understand what exercise to perform without scrolling

**Acceptance Criteria:**
- Card layout: Exercise name (24px bold) at top, GIF thumbnail (120px square) centered, target sets/reps below
- Tapping GIF → full-screen demo view with swipe-to-dismiss
- Exercise notes (if present) shown in collapsed accordion below card
- Matches Hevy's card visual hierarchy (reference: Behance search "Hevy app UI")
- Smooth transitions (200ms ease-in-out) between card states

**Implementation Notes:**
- Component: mindmirror-mobile/app/(app)/client/[id].tsx
- ~2-3 hours including design research

**Story Points:** 5

---

#### Story 2.2: Set Table Complete Overhaul
**As a** user
**I want** a clean, minimalist set table with clear previous/target/actual columns
**So that** logging sets feels effortless and I can track progression visually

**Acceptance Criteria:**
- Table columns: Set # | Previous | Target | Weight | Reps | ✓ (completion checkbox)
- Previous column shows greyed-out data from last workout (read-only)
- Target column shows prescribed sets/reps from program (read-only)
- Weight/Reps columns have numeric inputs with +/- stepper buttons
- Completion checkbox fills set row with success color (green tint)
- Auto-advance focus: Weight → Reps → Next set weight (keyboard flow)
- Matches Hevy's table density and spacing (compact but not cramped)

**Acceptance Criteria (Continued):**
- Previous workout data fetched via GraphQL query (historical practice_instance)
- Handles edge case: No previous workout exists (show "—" placeholder)

**Implementation Notes:**
- Requires schema verification for "previous workout" data retrieval (investigate historical practice_instance queries)
- ~3-4 hours for table layout + interaction logic

**Story Points:** 8

---

#### Story 2.3: Rest Timer as Modal
**As a** user
**I want** rest timer to appear as a modal overlay (not bottom sheet)
**So that** it's prominent, unignorable, and matches modern fitness app patterns

**Acceptance Criteria:**
- Timer triggers automatically after completing a set (checkbox checked)
- Modal appears centered with: circular progress ring, countdown (90s default), Skip/Add 30s buttons
- Background dimmed (80% opacity black overlay)
- Tapping outside modal does NOT dismiss (force user to interact with Skip)
- Haptic feedback at 10s, 5s, 0s remaining
- Matches Hevy's rest timer aesthetic (circular progress, bold countdown text)

**Implementation Notes:**
- Replace bottom sheet component with modal (react-native Modal or custom implementation)
- ~2 hours

**Story Points:** 5

---

#### Story 2.4: Notes Input for Sets/Exercises
**As a** user
**I want** to add notes about pain, form adjustments, or PRs after each set or exercise
**So that** I can track qualitative progress beyond just numbers

**Acceptance Criteria:**
- Notes icon button appears at set row level and exercise card level
- Tapping icon → text input modal with: "Add note" placeholder, 200 char limit, Save/Cancel buttons
- Saved notes appear as collapsed text below set/exercise with expand icon
- Notes persist to practice_instance.notes field (confirmed exists in schema)
- Notes visible in workout history view (future feature, just ensure data saves correctly)

**Implementation Notes:**
- Verify practice_instance.notes field mutation works (may need GraphQL schema extension if only exercise-level notes exist)
- ~1.5 hours

**Story Points:** 3

---

#### Story 2.5: Overall Visual Polish
**As a** user
**I want** workout screen to feel modern, professional, and motivating
**So that** I'm excited to use the app instead of reverting to pen-and-paper

**Acceptance Criteria:**
- Typography: System font stack (San Francisco on iOS, Roboto on Android), consistent sizing
- Color palette: Primary action blue (#4A90E2), success green (#7ED321), neutral grays (Hevy-inspired)
- Spacing: 16px padding standard, 8px between related elements, 24px between sections
- Shadows: Subtle elevation for cards (2dp elevation, 0.1 opacity)
- Animations: Fade-in for new exercises, slide-up for modals, spring physics for interactive elements
- Loading states: Skeleton screens for data fetching (no blank white screens)

**Implementation Notes:**
- Create design tokens file (colors, spacing, typography)
- Apply consistently across all workout UI components
- ~2-3 hours for design system setup + application

**Story Points:** 5

---

### Epic 3: Production Infrastructure Hardening

**Epic Goal:** Deploy secure, scalable production environment with modern Cloud Run v2 module and Supabase best practices.

---

#### Story 3.1: Cloud Run v2 Migration
**As a** platform engineer
**I want** production deployment to use google_cloud_run_v2_service module
**So that** we leverage latest GCP features (min instances, startup CPU boost, better logging)

**Acceptance Criteria:**
- infra/modules/practices/main.tf uses `google_cloud_run_v2_service` resource
- All services (agent, journal, habits, meals, movements, practices, users, gateway) migrated to v2
- Environment variables and secrets configuration equivalent to current setup
- Health checks configured with proper startup/liveness probes
- Min instances set to 1 for practices_service (prevent cold starts during alpha)
- Terraform plan shows clean migration (no resource recreation unless necessary)

**Implementation Notes:**
- Reference: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service
- Test in staging first, then production
- ~2 hours

**Story Points:** 5

---

#### Story 3.2: Supabase Separate Production Config
**As a** platform engineer
**I want** production environment to use dedicated Supabase project (not staging)
**So that** alpha user data is isolated and we can implement stricter security policies

**Acceptance Criteria:**
- New Supabase project created for production (separate from staging)
- Environment variables updated: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
- RLS policies enabled on vouchers table
- Auth configuration: Email confirmation required, JWT expiry 24 hours (vs 7 days staging)
- Separate OAuth providers (if needed for future social login)
- Terraform/automation creates Supabase resources (no manual ClickOps)

**Implementation Notes:**
- Use Supabase CLI for project bootstrapping: `supabase init`, `supabase db push`
- ~2 hours including policy setup

**Story Points:** 5

---

#### Story 3.3: Infrastructure Bootstrapping Automation
**As a** platform engineer
**I want** one-command deployment that provisions all GCP + Supabase resources
**So that** disaster recovery or new environment setup takes minutes, not hours

**Acceptance Criteria:**
- `make production-deploy` command runs: Terraform init → plan → apply → Supabase migrations
- Script validates prerequisites: gcloud auth, Terraform installed, Supabase CLI configured
- Idempotent: Running twice doesn't break existing resources
- Outputs critical values: Gateway URL, Database connection strings, Supabase project URL
- Rollback mechanism: `make production-rollback` reverts to previous Terraform state

**Implementation Notes:**
- Extend existing Makefile with production target
- ~2 hours for scripting + testing

**Story Points:** 3

---

#### Story 3.4: Security Hardening
**As a** security-conscious engineer
**I want** production secrets managed via Secret Manager with least-privilege IAM
**So that** API keys and DB credentials aren't exposed in environment variables or logs

**Acceptance Criteria:**
- All secrets (OPENAI_API_KEY, DATABASE_URL, Supabase keys) stored in Google Secret Manager
- Cloud Run services access secrets via volume mounts (not env vars)
- Service accounts have minimal IAM roles (practices_service → only practices DB access)
- Secrets rotated with version management (current + previous version available)
- No secrets in Terraform state file (use data sources, not resources)

**Implementation Notes:**
- Already partially implemented (infra/main.tf references google_secret_manager_secret)
- Audit and tighten IAM policies
- ~1 hour

**Story Points:** 2

---

### Epic 4: Alpha Testing Framework

**Epic Goal:** Create reproducible test scripts and validation checklist to catch regressions and streamline alpha user onboarding QA.

---

#### Story 4.1: Voucher Flow Manual Test Script
**As a** QA tester
**I want** step-by-step test script for voucher-based auto-enrollment flow
**So that** I can validate all 7 steps work correctly before inviting alpha users

**Acceptance Criteria:**
- Test script doc (Markdown) with steps:
  1. Generate magic link via admin UI
  2. Copy link to incognito browser
  3. Verify voucher minted (check Supabase vouchers table)
  4. Complete signup with matching email
  5. Login and verify program auto-assigned
  6. Navigate to workout screen, verify program visible
  7. Log 1 set, verify data saved
- Each step has: Expected result, Pass/Fail checkbox, Screenshot placeholder
- Edge cases covered: Mismatched email, expired voucher, duplicate enrollment
- Script executable by non-technical alpha tester (clear instructions, no jargon)

**Implementation Notes:**
- Save to docs/testing/voucher-flow-test-script.md
- ~1.5 hours to write + validate

**Story Points:** 3

---

#### Story 4.2: Workout Execution Regression Tests
**As a** developer
**I want** automated UI tests for workout logging critical path
**So that** future UI changes don't break set logging, rest timer, or notes functionality

**Acceptance Criteria:**
- Tests cover:
  - Load workout screen → exercises render
  - Log weight/reps → data persists after app restart
  - Complete set → rest timer modal appears
  - Add note to set → note saves to DB
  - Navigate away mid-workout → state persists on return
- Tests run in CI/CD pipeline (GitHub Actions or local pre-push hook)
- Uses Detox or Maestro for React Native E2E testing
- Test execution time <5 minutes

**Implementation Notes:**
- Detox setup: mindmirror-mobile/e2e/ directory
- May require test user accounts + test data seeding
- ~3-4 hours for framework setup + test authoring

**Story Points:** 8

---

#### Story 4.3: Alpha Validation Checklist
**As a** product manager
**I want** checklist tracking alpha user progress through onboarding + first 3 workouts
**So that** I know who's blocked and what features are causing friction

**Acceptance Criteria:**
- Checklist spreadsheet (Google Sheets) with columns:
  - Alpha user name, Email, Program assigned, Magic link sent (date), Signed up (Y/N), First workout completed (Y/N, date), Workouts completed (count), Bugs reported (list), Notes
- Pre-populated with 3 alpha users from docs/alpha-validation-week-1.md
- Shared with read/write access for PM and engineer
- Weekly snapshot saved to docs/testing/week-N-alpha-progress.md

**Implementation Notes:**
- Template provided in docs/week-1-execution-checklist.md (Tracking Spreadsheet Template section)
- ~0.5 hours to set up

**Story Points:** 1

---

### Epic 5: Alpha Monitoring & Support

**Epic Goal:** Implement error tracking and user activity monitoring to support alpha users in real-time and collect actionable feedback.

---

#### Story 5.1: Error Tracking Setup
**As a** developer
**I want** automatic error reporting from mobile app to centralized logging system
**So that** I know immediately when alpha users hit crashes or API errors

**Acceptance Criteria:**
- GCP Error Reporting integrated in mindmirror-mobile app (Sentry deferred to post-alpha)
- Errors captured: Unhandled exceptions, GraphQL query failures, network timeouts
- Error reports include: User ID, device info, breadcrumbs (last 10 actions), stack trace
- Alert threshold: >3 errors from same user within 1 hour → Slack notification
- Privacy: No PII logged (exclude email, names from error payloads)

**Implementation Notes:**
- GCP Error Reporting: ~30 min setup (lighter weight for alpha)
- Alternative: Sentry React Native SDK (~1 hour) if richer context needed
- Decision: GCP Error Reporting sufficient for alpha, defer Sentry to post-validation

**Story Points:** 2

---

#### Story 5.2: User Activity Monitoring Dashboard
**As a** product manager
**I want** dashboard showing alpha user engagement metrics
**So that** I can identify who's actively using the app vs. who needs follow-up

**Acceptance Criteria:**
- Dashboard shows per-user:
  - Last login (timestamp)
  - Workouts completed (count)
  - Workout completion rate (completed / scheduled)
  - Average session duration
  - Feature usage: Notes added (count), Rest timer used (count)
- Real-time updates (refresh every 5 minutes)
- Filter by user or date range
- Export to CSV for weekly review

**Implementation Notes:**
- Query practices_service for practice_instance data
- Build simple Next.js dashboard page at /admin/analytics
- ~2-3 hours

**Story Points:** 5

---

#### Story 5.3: Bug Triage Process Documentation
**As a** support engineer
**I want** documented process for triaging alpha user bug reports
**So that** critical issues get fixed same-day and minor issues are backlogged appropriately

**Acceptance Criteria:**
- Process doc (Markdown) with:
  - Bug severity levels: P0 (blocks workout), P1 (major friction), P2 (cosmetic)
  - Response SLAs: P0 (2 hours), P1 (24 hours), P2 (next sprint)
  - Bug report template for alpha users (what to include, how to share screenshots)
  - Escalation path: Who to notify for P0 bugs
- Shared in docs/testing/bug-triage-process.md
- Linked from alpha invite email ("Found a bug? Report it here")

**Implementation Notes:**
- ~1 hour to write
- Consider Google Form for structured bug submissions

**Story Points:** 1

---

## 7. PM Checklist Execution

### Quality Assurance Review

✅ **Goals clearly defined** - Section 1 states primary goal (validate voucher workflow with 3 alpha users) and success metrics (2+ workouts, <P1 bugs)

✅ **User personas identified** - Section 1 references 3 alpha user segments from brief (knee rehab, AC dysfunction, combat athlete)

✅ **Requirements are testable** - All FRs have acceptance criteria; NFRs have measurable thresholds (99% uptime, <200ms latency)

✅ **Technical assumptions validated** - Section 4 confirms codebase reality (notes field exists, auto-enroll mutation works, Cloud Run module confirmed)

✅ **Epics are scoped and estimated** - 5 epics with 19-36 hour total estimate, critical path identified

✅ **User stories follow format** - All stories use "As a [role], I want [goal], so that [benefit]" structure

✅ **Acceptance criteria are specific** - Each story has measurable, unambiguous success conditions

✅ **Dependencies mapped** - Epic 1 → Epic 2 → Epic 3 → Epic 4 critical path documented

✅ **Open questions documented** - Section 8 lists unresolved technical questions (workout state persistence, E2E framework choice, etc.)

✅ **Timeline aligns with constraints** - 4-week alpha validation window accommodated, Week 1 priorities match Monday deadline

✅ **Risks identified with mitigation** - Section 8 includes risk matrix with likelihood, impact, and mitigation strategies

✅ **Handoff prompts provided** - Section 9 includes detailed prompts for UX Expert, Platform Engineer, QA Engineer

### Story Point Summary

| Epic | Total Story Points | Estimated Hours |
|------|-------------------|-----------------|
| Epic 1: Admin Tooling | 6 | 2-4 hours |
| Epic 2: Workout UI/UX | 26 | 8-14 hours |
| Epic 3: Infrastructure | 15 | 4-8 hours |
| Epic 4: Testing Framework | 12 | 3-6 hours |
| Epic 5: Monitoring & Support | 8 | 2-4 hours |
| **TOTAL** | **67** | **19-36 hours** |

*Using Fibonacci sequence for story points: 1, 2, 3, 5, 8, 13*

---

## 8. Open Questions & Risks

### 8.1 Unresolved Technical Questions

**Q1: Workout State Persistence Mechanism**
- **Question:** Does workout duration + logged sets auto-save on navigation away, or require explicit save action?
- **Impact:** Critical for alpha UX (users will navigate away mid-workout)
- **Investigation needed:** Test app backgrounding, screen navigation, network interruption scenarios
- **Timeline:** Day 1 (before Epic 2 implementation)
- **Owner:** UX Expert / Mobile Engineer

**Q2: E2E Testing Framework Choice**
- **Question:** Detox (more mature) vs. Maestro (simpler setup) for React Native E2E tests?
- **Impact:** Affects Epic 4 implementation approach and CI/CD integration complexity
- **Tradeoffs:** Detox has steeper learning curve but better debugging; Maestro faster to set up but less flexible
- **Timeline:** Day 3 (before Epic 4 starts)
- **Owner:** QA Engineer

**Q3: "Previous Workout" Data Retrieval**
- **Question:** Does practices_service store historical practice_instance data for comparison in set table?
- **Impact:** Required for FR5 (set table previous column)
- **Investigation needed:** Query GraphQL schema for historical data endpoints, test data availability
- **Timeline:** Day 2 (before Epic 2 Story 2.2 implementation)
- **Owner:** Backend Engineer / Platform Engineer

**Q4: Notes Field Scope**
- **Question:** Is practice_instance.notes exercise-level only, or does it support set-level granularity?
- **Impact:** Affects FR7 implementation (notes input UI)
- **Investigation needed:** Verify GraphQL mutation accepts notes parameter, check schema flexibility
- **Timeline:** Day 1 (before Epic 2 Story 2.4 implementation)
- **Owner:** Backend Engineer

**Q5: Production Database Migration Strategy**
- **Question:** Blue/green deployment or maintenance window for Alembic migrations?
- **Impact:** Affects Epic 3 production deployment approach (zero-downtime vs. brief outage)
- **Tradeoffs:** Blue/green more complex but no downtime; maintenance window simpler but requires user communication
- **Timeline:** Week 2 (before production deployment)
- **Owner:** Platform Engineer

**Q6: GIF Demo Asset Storage**
- **Question:** Where are exercise GIF demos stored (GCS bucket, CDN, embedded in app)?
- **Impact:** Affects FR4 implementation (exercise card GIF thumbnail)
- **Investigation needed:** Check existing exercise data sources, identify GIF URLs
- **Timeline:** Day 2 (before Epic 2 Story 2.1 implementation)
- **Owner:** UX Expert / Backend Engineer

### 8.2 Project Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| Hevy UI cloning takes >14 hours due to design complexity | Medium | Medium | Set hard time cap at 12 hours; use design system library (NativeBase/Tamagui) to accelerate; accept "good enough" over "pixel-perfect" | UX Expert |
| Alpha user drops out before 3 workouts | Medium | High | Over-recruit 4th backup alpha user; incentivize with free 3-month subscription post-launch; follow up daily during Week 1 | PM |
| Cloud Run v2 migration breaks staging | Low | High | Test in isolated GCP project first; keep rollback Terraform state; run migration during low-traffic window | Platform Engineer |
| E2E test setup exceeds 4-hour estimate | Medium | Low | Defer automated tests to Week 2-3; rely on manual test scripts for Week 1 alpha invites; prioritize critical path coverage only | QA Engineer |
| Workout state doesn't persist on navigation | Low | Critical | Investigate immediately (Day 1); may require state management refactor (Zustand/Redux); consider this a Week 1 blocker if broken | UX Expert |
| Voucher flow breaks after production deployment | Low | Critical | Run full manual test script (Epic 4 Story 4.1) before sending alpha invites; validate in production environment, not staging | PM / QA Engineer |
| Alpha users report data loss bugs | Low | Critical | Implement defensive logging for all mutations; enable Supabase audit logs; ensure database backups configured | Platform Engineer |
| Notes field mutation not implemented | Medium | Low | Backend engineer adds mutation if needed (1-2 hours); defer notes feature to Week 2 if complex | Backend Engineer |
| Design system library conflicts with existing styles | Medium | Medium | Create isolated components for workout UI; avoid global style overrides; test on both iOS and Android | UX Expert |
| Production budget exceeds $100/month | Low | Low | Monitor GCP billing daily during Week 1-2; set budget alerts at $75; scale down min instances if needed | Platform Engineer |

### 8.3 Decision Points

**Week 1 Decision: Ship Workout UI "Good Enough" vs. Delay Alpha Invites**
- **Criteria:** If Epic 2 exceeds 14 hours by Day 5, do we ship imperfect UI or delay Monday invite?
- **Recommendation:** Ship "good enough" (functional + 70% polished) over delaying alpha invites
- **Rationale:** Alpha users expect rough edges; feedback on functional issues more valuable than pixel-perfect UI

**Week 2 Decision: Production Deployment Timing**
- **Criteria:** Deploy before Alpha User 1 invite (Day 4) or use staging?
- **Recommendation:** Deploy production by Week 2 Day 3 (1 day buffer)
- **Rationale:** Real user data should never touch staging environment; production isolation critical for security

**Week 4 Decision: Green/Yellow/Red Light for Broader Rollout**
- **Criteria:** See Section 1.4 Success Metrics
- **Green light actions:** Finish UYE PDF, scale up Facebook ads, recruit 10-20 Reddit beta testers
- **Yellow light actions:** Fix P1 bugs, iterate UX based on feedback, recruit 2-3 more alpha users for validation
- **Red light actions:** Conduct user interviews to identify fundamental issues, consider pivot to single vertical (adaptive coaching vs. marketplace)

---

## 9. Next Steps & Handoff Prompts

### 9.1 For UX Expert (Workout UI Implementation)

**Context:**
You're implementing a workout execution interface overhaul to match Hevy's aesthetic. The current UI is functional but lacks polish. You have 8-14 hours to redesign exercise cards, set table, rest timer, and notes input.

**Reference Materials:**
- Current implementation: `mindmirror-mobile/app/(app)/client/[id].tsx`
- Hevy UI inspiration: Search Behance/Dribbble for "Hevy workout app UI"
- Design requirements: Epic 2 stories (2.1-2.5) in this PRD (Section 6)
- UI Design Goals: Section 3 of this PRD

**Key Design Constraints:**
- Must work on iOS and Android (React Native)
- Accessibility: Minimum touch target 44px, WCAG AA color contrast
- Performance: List virtualization for programs with >20 exercises
- Offline-first: Optimistic UI updates, sync when network available

**Critical Investigation (Day 1 Priority):**
- **Workout state persistence:** Test if duration + sets persist when user navigates away. If broken, may need state management refactor (Zustand/Redux).
- **Notes field scope:** Verify if practice_instance.notes supports set-level granularity or exercise-level only. Check GraphQL mutation.
- **Previous workout data:** Confirm GraphQL query can fetch last workout's sets for same exercise (needed for set table "Previous" column).
- **GIF demo assets:** Identify where exercise GIF URLs are stored (GCS bucket, CDN, embedded).

**Deliverables:**
1. Design tokens file (colors, typography, spacing) - Day 1
2. Component refactor for exercise cards, set table, rest timer modal, notes input - Days 2-4
3. Screenshots of before/after for PM review - Day 5
4. Code commit with clear PR description linking to Epic 2 stories - Day 5

**Open Questions for You:**
- Should set table support superset/circuit grouping (future feature)?
- Preference for animation library (React Native Reanimated vs. Animated API)?
- Do we need dark mode support for alpha, or defer to post-validation?
- Use NativeBase, Tamagui, or custom components?

**Success Criteria:**
- PM can complete full workout using new UI without confusion (dogfooding test)
- Set logging feels as smooth as Hevy (subjective but aim for <5s per set)
- Rest timer modal is unignorable (users don't accidentally skip rest periods)
- No visual regressions on iOS and Android

---

### 9.2 For Platform Engineer (Infrastructure Hardening)

**Context:**
You're deploying a production environment for 3 alpha users starting Week 2. Current staging uses google_cloud_run_service (v1), and we need to migrate to v2 while adding Supabase production isolation and security hardening.

**Reference Materials:**
- Current infra: `infra/main.tf`, `infra/modules/practices/main.tf`
- Cloud Run v2 docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service
- Requirements: Epic 3 stories (3.1-3.4) in this PRD (Section 6)
- Technical Assumptions: Section 4 of this PRD

**Key Infrastructure Constraints:**
- Budget: <$100/month for alpha (3 users, low traffic)
- Regions: us-central1 (primary), us-east1 (failover for future)
- Secrets: Google Secret Manager only (no .env files in production)
- Databases: Separate Supabase project from staging
- Timeline: Production deployed by Week 2 Day 3 (before Alpha User 1 invite Day 4)

**Critical Tasks:**
1. **Cloud Run v2 migration** (Story 3.1) - Test in isolated GCP project first
2. **Supabase production project** (Story 3.2) - RLS policies + JWT expiry 24h + email confirmation
3. **One-command deployment** (Story 3.3) - `make production-deploy` with validation checks
4. **Security audit** (Story 3.4) - Secrets via volume mounts, least-privilege IAM, no secrets in Terraform state

**Deliverables:**
1. Terraform refactor for Cloud Run v2 (all 7 services + gateway) - Week 1-2
2. Supabase production project with RLS policies - Week 2
3. `make production-deploy` command with validation checks - Week 2
4. Runbook for rollback procedure (docs/infrastructure/production-rollback.md) - Week 2

**Open Questions for You:**
- Should we enable Cloud CDN for static assets (web app)?
- VPC peering needed between Cloud Run and Cloud SQL, or public IP acceptable for alpha?
- Preference for Terraform Cloud vs. local state with GCS backend?
- Blue/green deployment or maintenance window for Alembic migrations?

**Success Criteria:**
- Production deployment completes in <10 minutes (one command)
- Zero downtime for future deployments (or documented maintenance window process)
- PM can access admin UI at production URL with Supabase auth
- GCP billing <$100/month during Week 1-4 alpha period

---

### 9.3 For QA Engineer (Alpha Testing Framework)

**Context:**
You're creating manual test scripts and E2E test foundation for voucher-based auto-enrollment flow and workout execution. Tests must be reproducible and eventually automatable.

**Reference Materials:**
- Test requirements: Epic 4 stories (4.1-4.3) in this PRD (Section 6)
- Voucher flow: docs/alpha-validation-week-1.md (7-step breakdown)
- Current mobile app: `mindmirror-mobile/`
- Week 1 checklist: docs/week-1-execution-checklist.md

**Key Testing Constraints:**
- Manual tests must be executable by non-technical PM
- E2E tests should run in CI/CD within 5 minutes
- Test data: Use dedicated test Supabase accounts (not production alpha users)
- Edge cases: Mismatched email, expired voucher, duplicate enrollment, network failure
- Timeline: Manual test script ready by Day 3, E2E tests by Week 2-3

**Critical Tasks:**
1. **Manual test script** (Story 4.1) - Voucher flow 7 steps + edge cases, Markdown doc
2. **E2E test framework** (Story 4.2) - Detox vs. Maestro decision + setup + workout logging tests
3. **Alpha validation checklist** (Story 4.3) - Google Sheets with 3 alpha users pre-populated

**Deliverables:**
1. Manual test script (docs/testing/voucher-flow-test-script.md) - Day 3
2. E2E test framework setup (Detox or Maestro) - Week 2
3. Automated tests for workout logging critical path - Week 2-3
4. Alpha validation checklist spreadsheet (Google Sheets) - Day 3

**Open Questions for You:**
- Should we record test execution videos (Loom) for PM review?
- Preference for Detox (more mature) vs. Maestro (simpler setup)?
- Do we need API contract tests (GraphQL schema validation), or defer to post-alpha?
- Should E2E tests run on every commit or just pre-release?

**Success Criteria:**
- PM can execute manual test script in <30 minutes (including screenshots)
- E2E tests catch set logging regression before code reaches production
- Alpha validation checklist shows clear picture of who's blocked and why
- Zero P0 bugs reach alpha users (caught by manual test script before invites)

---

### 9.4 For Backend Engineer (GraphQL Schema Validation)

**Context:**
The UX Expert needs clarification on GraphQL schema capabilities before implementing notes input (FR7) and set table previous column (FR5).

**Investigation Tasks:**
1. **Notes field mutation** - Does `updatePracticeInstance` mutation accept `notes` parameter? Test with GraphQL Playground.
2. **Set-level notes** - Is practice_instance.notes exercise-level only, or can we support set-level granularity? May need schema extension.
3. **Historical data query** - Can we query previous workout's sets for same exercise? Needed for set table "Previous" column.
4. **GIF demo URLs** - Where are exercise GIF assets stored? GCS bucket path or CDN URL pattern?

**Deliverables:**
- Document GraphQL query/mutation examples for UX Expert (Day 1)
- If notes mutation missing, implement it (estimated 1-2 hours)
- If historical data query complex, provide helper resolver (estimated 1-2 hours)

**Timeline:** Day 1 (blocker for Epic 2 Stories 2.2 and 2.4)

---

## 10. Appendix

### 10.1 Glossary

- **Alpha User:** Early tester providing feedback during validation phase (3 users total)
- **Auto-enrollment:** Voucher-triggered program assignment upon user signup
- **Magic Link:** One-click authentication URL with embedded voucher for frictionless onboarding
- **Practice Instance:** Database record representing a single workout session
- **Voucher:** Token granting user access to specific program (embedded in magic link)
- **P0/P1/P2 Bugs:** Priority levels (P0 = critical/blocking, P1 = major friction, P2 = cosmetic)
- **Cloud Run v2:** Google Cloud's next-generation serverless container platform
- **RLS (Row-Level Security):** Supabase/Postgres feature enforcing data access policies at DB level

### 10.2 References

- Project Brief: `docs/brief.md`
- Alpha Validation Strategy: `docs/alpha-validation-week-1.md`
- Week 1 Execution Checklist: `docs/week-1-execution-checklist.md`
- Brainstorming Session Results: `docs/brainstorming-session-results.md`
- Architecture: `docs/architecture.md` (if exists)
- CLAUDE.md: Project instructions for Claude Code

### 10.3 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v4 (Draft) | 2025-10-15 | PM Agent (John) | Initial PRD creation for alpha validation initiative |

---

**End of PRD**

*For questions or feedback, contact PM Agent (John) or submit issue to project tracker.*
