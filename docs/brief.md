# Project Brief: Swae OS Soft Launch

**Version:** 1.0
**Date:** 2025-10-15
**Author:** Product Manager (John)

---

## Executive Summary

Swae OS Soft Launch is a 4-week alpha validation initiative to stress test the existing voucher-based workout program infrastructure with 3 real users before scaling to broader audiences. The platform enables coaches to send magic links that automatically mint vouchers, create user accounts, and assign personalized workout programs—requiring zero manual intervention. This soft launch targets three distinct user segments (knee rehab, postural dysfunction, and combat athletes) to validate the end-to-end flow from link click to workout completion, identify critical bugs, and determine which demographic shows the strongest product-market fit signals for future focus.

---

## Problem Statement

MindMirror has built 85% of the technical infrastructure needed to onboard users into personalized workout programs via a 7-step voucher system (magic link generation → auto-enrollment → program visibility). However, **this infrastructure has never been validated with real users in real conditions.**

### Current State & Pain Points

1. **Unvalidated Critical Path:** The voucher flow works for habits and lessons, but workout program auto-enrollment (via `practices_service`) has only been tested internally. We don't know if it will break under real user behavior (duplicate link clicks, email mismatches, mid-workout exits, offline scenarios).

2. **UI/UX Unknowns:** Step 7 (workout execution—logging sets, reps, rest periods) exists but needs polish. We don't know where users will get confused, frustrated, or drop off until they actually use it.

3. **No Product-Market Fit Signal:** Three distinct user segments have been identified (knee rehab, postural dysfunction, combat athletes), but we have zero data on which demographic will engage most strongly. Building the wrong programs or targeting the wrong audience post-alpha would waste months.

4. **Risk of Premature Scaling:** Plans exist for PDF sales funnels, Reddit beta testing, and Facebook ads—but launching these before validating the core flow could result in paying to acquire users who hit broken onboarding, leading to high churn and wasted ad spend.

### Impact of the Problem

- **Technical Risk:** Critical bugs (data loss, crashes, enrollment failures) discovered after scaling would require emergency fixes and damage user trust
- **Strategic Risk:** Picking the wrong demographic to focus on (Month 3-6 roadmap) without alpha validation could result in building features nobody wants
- **Opportunity Cost:** Every week spent building without user feedback is a week of building potentially wrong things

### Why Now

The Monday alpha invite deadline creates urgency: we need to validate the infrastructure before committing to broader validation strategies (Reddit, ads, PDF sales). Waiting longer delays the entire Month 1-3-6 roadmap.

---

## Proposed Solution

The Swae OS Soft Launch executes a structured 4-week alpha validation program with 3 real users across distinct use cases, following a **stress test → fix → onboard → validate → decide** workflow:

### Core Approach

**Week 1: Infrastructure Stress Testing & Onboarding**
- **Days 1-2:** Systematic stress testing of the 7-step voucher flow with test accounts, documenting all bugs and edge cases (duplicate link clicks, email mismatches, offline scenarios, mid-workout exits)
- **Day 3:** Fix all **critical** bugs (crashes, data loss, enrollment failures); defer polish items to Week 2
- **Day 4:** Invite User 1 (knee rehab program already built) with magic link
- **Day 5:** Monitor User 1's first workout, collect immediate feedback, fix urgent blockers
- **Days 6-7:** Build programs for Users 2 & 3 (AC dysfunction, combat athlete), send invites

**Weeks 2-4: Engagement Validation & Strategic Decision**
- **Week 2:** Daily check-ins with Users 1-2, weekly check-in with User 3; fix bugs discovered in Week 1; polish UX based on feedback
- **Week 3:** Test program progression (does app advance users to next phase automatically?); track adherence patterns
- **Week 4:** Decision point—analyze which demographic showed strongest engagement signals to inform Month 3-6 focus

### Key Differentiators

1. **Structured Testing Workflow:** Unlike typical "ship and pray" alpha launches, this approach systematically validates infrastructure before exposing users to it, reducing risk of damaging first impressions

2. **Multi-Segment Hedging:** Testing three distinct demographics (rehab, postural, combat sports) simultaneously provides fallback options and early product-market fit signals

3. **Decision Framework Built-In:** Week 4 includes explicit gut-check criteria (Would they pay $25/month? Would they recommend to friends? Did measurable results occur?) to inform future strategic direction

4. **Repeatability-First Tooling:** Admin UI for magic link generation (extending existing `web/` admin assets) ensures testing workflow can be re-run in <5 minutes and eventually automated—critical for future cohort onboarding

### Why This Solution Will Succeed

- **85% infrastructure already exists:** We're validating, not building from scratch—reduces timeline and technical risk
- **Small, focused cohort:** 3 users is manageable for close monitoring while providing diverse signal
- **Hard deadline creates urgency:** Monday alpha invites force disciplined execution
- **Tight feedback loop:** Daily/weekly check-ins ensure issues are caught and fixed in real-time, not discovered weeks later

### High-Level Vision

If alpha validation succeeds (3/3 users sign up, complete workouts, provide positive feedback), the infrastructure is proven ready for Month 2-3 scaling strategies (Reddit beta testing, PDF sales funnels, Facebook ads). If validation reveals critical gaps, we fix them before broader launch—saving months of potential wasted effort.

---

## Target Users

### Primary User Segment: Rehab & Pain Management (User 1)

**Profile:**
- **Demographics:** Female, 50+ years old, sedentary to moderately active
- **Presenting Issue:** Patellofemoral pain syndrome (knee pain)
- **Current Behaviors:** Likely tried physical therapy, YouTube exercises, or generic fitness apps but needs structured, progressive rehab programming
- **Tech Comfort:** Moderate—can use smartphone apps but needs intuitive UI

**Specific Needs & Pain Points:**
- **Guided progression:** Needs to know which exercises to do, in what order, and when to advance
- **Pain tracking:** Must be able to log subjective pain levels (1-10 scale) to understand if program is working
- **Accountability:** Daily check-ins (in-person or text) to maintain adherence
- **Simplicity:** Can't be overwhelmed with too many features—just show me today's workout

**Goals:**
- Reduce knee pain from 8/10 → 5/10 or lower within 4 weeks
- Regain functional movement (stairs, squats, daily activities) without pain
- Avoid surgery or expensive ongoing physical therapy

**Why This Segment First:**
- **Program already built:** Knee rehab program exists and is ready to test
- **High urgency:** Pain is immediate and motivating—strong adherence signal
- **Clear success metric:** Measurable pain reduction validates program efficacy

---

### Secondary User Segment: Postural Dysfunction / Desk Workers (User 2)

**Profile:**
- **Demographics:** Male or female, 30-50 years old, desk job
- **Presenting Issue:** Anterior bias → acromioclavicular (AC) dysfunction, likely originating from lumbopelvic misalignment
- **Current Behaviors:** Sporadic stretching, maybe some gym work, but no structured corrective program
- **Tech Comfort:** High—comfortable with apps and tech solutions

**Specific Needs & Pain Points:**
- **Root cause correction:** Needs exercises targeting lumbar stability, not just shoulder stretches
- **Exercise clarity:** Video demos and coaching cues ("Keep ribs down, don't flare") to perform movements correctly
- **Progress visibility:** Wants to see shoulder pain reduction and functional improvement over time
- **Flexibility:** Needs program that fits around work schedule

**Goals:**
- Reduce shoulder dysfunction and improve posture awareness
- Build sustainable movement habits that prevent recurrence
- Avoid needing ongoing chiropractic or PT appointments

**Why This Segment:**
- **Large addressable market:** Desk workers with postural issues are everywhere
- **Tests exercise library:** Requires clear video demos and coaching cues—validates content quality
- **Tests program complexity:** Multi-phase progression (lumbar stability → shoulder integration → load progression)

---

### Secondary User Segment: Combat Athletes / Strength Training (User 3)

**Profile:**
- **Demographics:** Male or female, 20-40 years old, trains BJJ, boxing, Muay Thai, or MMA 3-6x/week
- **Presenting Issue:** Needs strength & conditioning program that complements skill training without interfering with performance
- **Current Behaviors:** Likely follows generic barbell programs (e.g., Starting Strength, 5/3/1) but needs sport-specific adaptation
- **Tech Comfort:** High—expects modern app experience with workout logging, rest timers, progressive overload tracking

**Specific Needs & Pain Points:**
- **Training integration:** Can't be fried for skill work—volume must be moderate, recovery must be prioritized
- **Workout logging:** Needs to track sets, reps, weight, and rest periods for progressive overload
- **Flexibility:** Gym equipment varies—needs exercise swap options (e.g., trap bar → conventional deadlift)
- **Injury prevention:** Emphasize neck strength, posterior chain, anti-rotation core for combat sports durability

**Goals:**
- Build strength without mass gain (stay in weight class)
- Reduce injury risk from combat training
- Track progressive overload to ensure program is working

**Why This Segment:**
- **Highest expected engagement:** Intrinsically motivated, already trains 3-6x/week, part of tight gym communities
- **Tests advanced features:** Rest timers, weight tracking, exercise swaps—most complex UI validation
- **Easiest to recruit more users:** If User 3 engages, can bring 10-20 training partners for beta testing

---

## Goals & Success Metrics

### Business Objectives

- **Validate voucher infrastructure with zero critical bugs:** Complete 3 end-to-end user journeys (magic link → signup → workout completion) with no data loss, crashes, or enrollment failures by Week 1 Day 7
- **Achieve 100% alpha onboarding rate:** 3/3 invited users successfully sign up and complete at least 1 workout by Week 1 end
- **Establish strategic direction for Month 3-6:** Identify which user segment (rehab, postural, combat sports) shows strongest engagement signals (adherence, satisfaction, willingness to pay) by Week 4 end
- **Build repeatable testing infrastructure:** Create admin UI for magic link generation that enables full alpha workflow re-execution in <5 minutes by Week 1 Day 3
- **Maintain project velocity:** Complete all Week 1 deliverables (stress testing, bug fixes, onboarding, program creation) within 5-day timeline to hit Monday alpha invite deadline

### User Success Metrics

- **Onboarding completion rate:** 100% of invited users complete signup and see their assigned program (validates Steps 1-6 of voucher flow)
- **Workout completion rate:** ≥80% of users complete ≥3 workouts by Week 2 end (validates Step 7 UI usability)
- **Adherence rate (Week 2-4):** Users complete ≥50% of assigned workouts (validates program stickiness)
- **Subjective satisfaction:** ≥2/3 users report positive feedback ("I'd actually use this regularly") by Week 4
- **Pain/progress outcomes:**
  - User 1 (knee): Pain reduction ≥30% (e.g., 8/10 → 5/10 or lower) by Week 4
  - User 2 (posture): Reports noticeable shoulder improvement or posture awareness by Week 4
  - User 3 (combat): Completes workouts without interfering with skill training, reports strength gains by Week 4

### Key Performance Indicators (KPIs)

| KPI | Target | Measurement Method |
|-----|--------|-------------------|
| **Critical bugs discovered** | 0 by Week 1 Day 7 | Manual testing + user reports |
| **Alpha invite success rate** | 3/3 (100%) | Database check: user signup + program enrollment |
| **Week 1 workout completion** | 3/3 users complete ≥1 workout | Database logs + user check-ins |
| **Week 2-4 adherence rate** | ≥50% of assigned workouts completed | Database logs: workouts_completed / workouts_assigned |
| **Bug report volume** | <5 non-critical bugs per user over 4 weeks | Tracking spreadsheet from user feedback |
| **Time-to-resolution (critical bugs)** | <24 hours from discovery | Git commit timestamps + deployment logs |
| **Admin workflow efficiency** | Generate + send magic link in <2 minutes | Manual timing of admin UI workflow |
| **User Net Promoter Score (NPS)** | ≥2/3 users would recommend (informal gut-check) | Week 4 interview: "Would you recommend to friends?" |
| **Strategic clarity** | 100% confidence in Month 3-6 demographic focus | Week 4 decision framework: engagement, outcomes, scalability |

---

## MVP Scope

### Core Features (Must Have)

**1. Admin UI for Magic Link Generation**
- **Description:** Extend existing admin assets in `web/` subdirectory to provide a simple UI for generating custom magic links for alpha users. UI must allow selection of user email, program ID, and generation of embeddable voucher link. This ensures repeatable testing workflow (<2 minutes per link) and sets foundation for future automation.
- **Rationale:** User explicitly flagged need for "super ergonomic" way to run tests that's "really, really, really fucking easy to re-do later." Without this, alpha testing becomes manual, error-prone, and non-repeatable.

**2. Systematic Infrastructure Stress Testing (Days 1-2)**
- **Description:** Execute 8 predefined test rounds covering happy path, edge cases (duplicate clicks, email mismatches, offline mode, mid-workout exits), and UX friction points. Document all bugs with severity classification (Critical/High/Medium/Low) in tracking template.
- **Rationale:** 85% of infrastructure exists but has never been validated with real user behavior patterns. Systematic testing prevents discovering critical bugs after users are onboarded.

**3. Critical Bug Fixes (Day 3)**
- **Description:** Fix ALL bugs classified as Critical (crashes, data loss, enrollment failures) before inviting User 1. High/Medium/Low severity bugs can be deferred to Week 2 polish phase.
- **Rationale:** First impressions matter—cannot expose alpha users to showstopper bugs that damage trust or block workflow completion.

**4. Workout UI Polish (Step 7)**
- **Description:** Improve workout execution interface to ensure users can log sets, reps, rest periods without confusion or frustration. Focus on clarity (obvious buttons), visibility (rest timer prominent), and data persistence (partial progress saves if user exits mid-workout).
- **Rationale:** Steps 1-6 (voucher flow) are 85% complete; Step 7 (workout execution) is the primary UI work required for alpha readiness.

**5. Workout Program Creation for Users 2 & 3 (Days 6-7)**
- **Description:** Build AC dysfunction program (3 phases: lumbar stability → shoulder integration → load progression) and combat athlete barbell program (2-3x/week strength focus) in `practices_service`. Programs must be visible in app and assignable via voucher system.
- **Rationale:** User 1's knee program already exists; Users 2-3 programs must be created to enable Week 1 Day 7 invites.

**6. Daily/Weekly Check-In Workflow**
- **Description:** Establish lightweight feedback collection cadence: Users 1-2 receive daily text/in-person check-ins ("How was today's workout? Anything broken?"), User 3 receives weekly check-ins. Track responses in simple spreadsheet (user, date, workout completed, pain level, bugs reported, feature requests).
- **Rationale:** Alpha testing requires tight feedback loop to catch issues early. Spreadsheet ensures no feedback is lost.

**7. Week 4 Decision Framework Execution**
- **Description:** At Week 4 end, analyze alpha data against decision criteria: engagement (adherence rate, workout completion), outcomes (pain reduction, strength gains, satisfaction), and scalability (would they recommend? easy to recruit more users?). Document which demographic to focus on for Month 3-6.
- **Rationale:** Alpha validation must inform strategic direction—without explicit decision framework, we risk analysis paralysis or gut-feel decisions without data.

**8. Production Environment Creation (High Priority)**
- **Description:** Duplicate staging Tofu/Terraform configuration to create separate production Cloud Run deployment with new Supabase config, improved lockdown, and performance tuning. Alpha users may be onboarded to staging initially, then migrated to production.
- **Rationale:** Best practice to separate staging and production; enables safe experimentation in staging without risking production stability.

**9. Workout State Persistence Investigation**
- **Description:** Verify that navigating away from workout mid-session saves current state (duration elapsed, sets completed) to enable restart on same device or different device. If not implemented, add logic to persist workout state on navigation events.
- **Rationale:** Critical UX issue—users will lose trust if workout progress disappears when they exit mid-session.

**10. Pain/Progress Notes Input**
- **Description:** Add optional text input field near "Complete Workout" button in workout UI to capture user notes (pain levels, energy, subjective feedback). Data persists to database for later analysis.
- **Rationale:** Alpha validation requires qualitative feedback beyond quantitative logs (sets, reps); embedded input reduces friction vs. separate form.

---

### Out of Scope for MVP

- **PDF sales funnels:** No landing pages, no Stripe integration, no post-purchase email automation—validation comes first
- **Reddit beta testing:** No community posts, no beta user recruitment beyond the 3 alpha users
- **Facebook ads:** No ad creative, no campaign setup, no spend—premature until infrastructure is validated
- **Agent service rebuild:** No LangGraph template merge, no onboarding interview bot, no AI weekly summaries
- **Nutrition/meals integration:** No meal logging, no CV-based tracking, no macro summaries—workout validation only
- **New feature development:** No habit daily variations, no journal prompt scheduling, no assessments service
- **GitOps/CI/CD improvements:** Manual deployments acceptable for alpha; automation can wait until Month 2
- **Design overhaul:** Functional UI is sufficient; polish and branding defer to post-alpha
- **Additional user segments:** No backup User 4 recruitment unless one of the primary 3 drops out
- **Cloud Run Tofu module upgrade (v2):** Defer to post-alpha infrastructure work

---

### MVP Success Criteria

**Alpha validation is successful if:**
- ✅ 3/3 users successfully sign up via magic links (validates Steps 1-6)
- ✅ 3/3 users complete ≥1 workout with no critical bugs (validates Step 7)
- ✅ 0 critical bugs exist by Week 1 Day 7 (validates infrastructure hardening)
- ✅ Admin UI enables magic link generation in <2 minutes (validates operational repeatability)
- ✅ ≥2/3 users complete ≥50% of assigned workouts by Week 4 (validates engagement)
- ✅ Clear strategic decision documented by Week 4 (validates decision framework)

**Alpha validation fails if:**
- ❌ Any user cannot complete signup or see assigned program (critical infrastructure failure)
- ❌ Data loss or crashes occur during workouts (critical UX failure)
- ❌ <2/3 users engage beyond Week 1 (indicates product-market fit issue)
- ❌ Unable to determine strategic direction by Week 4 (indicates insufficient signal)

---

## Post-MVP Vision

### Phase 2 Features (Month 2: Post-Alpha Scaling)

**If alpha validation succeeds, immediately prioritize:**

**1. Revenue Infrastructure**
- **Stripe Integration:** Payment processing, webhooks (payment success → voucher generation), subscription billing
- **PDF Generation Pipeline:** Convert program content (e.g., Unfuck Your Eating) to professional PDFs using Pandoc or Canva
- **Post-Purchase Email Automation:** Leverage existing Supabase Edge Functions to send PDF + magic link in single email after payment
- **Rationale:** "Flip the switch" monetization—once validation succeeds, want to capture revenue immediately

**2. Beta User Recruitment**
- **Reddit Beta Launch:** Post in 5-10 communities (r/loseit, r/fitness, r/bjj, r/amateur_boxing) offering free beta access via voucher system
- **Facebook Ads Test:** $500 ad spend to UYE landing page (waitlist), track CTR, CPL, conversion rate
- **Manual Onboarding:** 10-20 free beta testers to stress test infrastructure at moderate scale
- **Rationale:** Alpha proves infrastructure works with 3 users; beta proves it works with 20+ before scaling further

**3. GitOps/CI/CD (Weeks 5-7)**
- **CI/CD Automation:** Detect code changes → rebuild containers → generate Terraform plan → manual approval → deploy
- **Scope:** 80% automation (not 100%)—acceptable for <100 users
- **Rationale:** Manual deployments acceptable for alpha (<12 users); automation required before scaling to dozens/hundreds

---

### Long-Term Vision (Month 3-6: Validation Mode → Differentiation Mode)

**Month 3 Direction (250 Users - "Validation Mode"):**

**Core Value Proposition:** "If you use the app, you don't have to think. The program just works."

- **PDF-to-Program Conversion:** Static PDFs become living, scheduled programs auto-loaded daily
- **Frictionless Tracking:** Workout logging, habit check-ins (yes/no), meal logging with minimal input
- **Progress Visualizations:** Charts for adherence, macros, workout progression, habit streaks
- **AI Weekly Summaries:** LLM-generated progress reviews across workouts, habits, journals
- **Agent Service Template Merge:** Port existing agent logic into modern LangGraph + FastAPI reference template (1-2 weeks vs. 4-8 weeks full rebuild)

**Month 6 Direction (Differentiation Mode - "Competitive Moat"):**

**Core Value Proposition:** "MyFitnessPal/Future/Caliber can't do this—we have unified data + agent orchestration."

- **Multi-Agent Adaptive Planning:** Specialized agents (nutritionist, coach, behavior specialist) analyze holistic data (meals, workouts, journals, sleep, menstrual cycles) → generate truly adaptive programs
- **Ambient Agents:** Auto-trigger actions based on environmental context (e.g., "Slept poorly → shift to lighter workout today")
- **Deep Research Agents:** Analyze cross-vertical patterns ("You journal more positively on days you eat protein-rich breakfasts")
- **Graph Database Migration:** Postgres → MemGraph/Neo4j for richer relational data modeling
- **CV-Based Meal Logging:** Photo + caption → composition analysis (holistic patterns, not precise macros)

**Strategic Rationale:**
- **Month 1:** Prove infrastructure works (alpha validation)
- **Month 2:** Prove demand exists (beta + revenue)
- **Month 3:** Prove stickiness ("app makes life easier" → daily active usage)
- **Month 6:** Prove differentiation ("no competitor can replicate this" → competitive moat)

---

### Expansion Opportunities

**Demographic Expansion (Based on Alpha Winner):**
- **If combat sports wins:** Build 3-5 more combat-specific programs (striker S&C, grappler strength, shoulder health for boxers), recruit 10-20 beta testers from local gyms, create content marketing (blog, Reddit outreach)
- **If 50+ rehab wins:** Build 3-5 joint-friendly programs (hip mobility, balance/fall prevention, bone density), recruit via Facebook ads or doctor referrals, position as healthcare expense ($20-30/month)
- **If postural/desk workers win:** Build corporate wellness partnerships, target remote work communities, emphasize "undo 8 hours of sitting" messaging

**Product Vertical Expansion:**
- **Nutrition First:** Leverage Unfuck Your Eating (UYE) program as second product—test with alpha users after 3-5 days of workout usage
- **Habits Integration:** Daily habit variations + journal prompt scheduling (already scoped in brainstorming results)
- **Mindfulness/Practices:** Meditation programs paired with workout programs for holistic wellness

**Platform Expansion:**
- **Coach-Client B2B:** Enable coaches to create programs for clients at scale (not just self-serve)
- **Marketplace Model:** Subscription unlocks all programs in marketplace ($30-50/month) vs. individual program purchases
- **Enterprise Partnerships:** Corporate wellness programs, gym partnerships, physical therapy clinic integrations

---

## Technical Considerations

### Platform Requirements

**Target Platforms:**
- **Mobile:** React Native (Expo) - iOS and Android via single codebase
- **Web Admin:** Next.js web app (existing admin assets in `web/` subdirectory)
- **Backend Services:** Python FastAPI microservices (federated GraphQL via Hive Gateway)

**Environment:**
- **Development:** Docker Compose (`make demo`) - full local stack with PostgreSQL, Qdrant, Redis
- **Alpha Deployment:** Cloud Run staging environment (may migrate to new production environment mid-alpha)
- **Browser/OS Support:** Modern browsers (Chrome, Safari, Firefox); iOS 14+, Android 10+

**Performance Requirements:**
- **Magic link generation:** <2 seconds from admin UI button click to link display
- **Voucher minting:** <3 seconds from link click to voucher creation in database
- **Workout data save:** <1 second from "complete set" button tap to database write
- **App load time:** <2 seconds from launch to home screen (acceptable for alpha)

---

### Technology Stack

**Frontend:**
- **Mobile App:** React Native (Expo) with TypeScript, Apollo Client for GraphQL, Supabase Auth
  - **Existing:** `mindmirror-mobile/` codebase with workout UI at `app/(app)/client/[id].tsx`
- **Web Admin:** Next.js with TypeScript, Apollo Client
  - **Existing:** Admin assets in `web/` subdirectory - extend for magic link generation UI
  - **Mode:** `NEXT_PUBLIC_APP_MODE=demo` for full features (local dev)

**Backend:**
- **Services:** Python FastAPI with async/await, SQLAlchemy ORM
  - **Existing Services:** Agent (port 8000), Journal (8001), Habits (8003), Meals (8004), Movements (8005), Practices (8006), Users (8007)
  - **Focus for Alpha:** Practices service (workout programs) + voucher/auto-enrollment logic
- **API Gateway:** GraphQL Hive Gateway (port 4000) - federates all microservice schemas
- **Background Jobs:** Fire-and-forget synchronous service calls for reindexing (future: GCP Pub/Sub event-driven)

**Database:**
- **Primary:** PostgreSQL 14+ (async via asyncpg)
  - **Main DB (port 5432):** Agent, Journal, Habits services
  - **Separate DBs:** Movements (5435), Practices (5436), Users (5437)
- **Vector DB:** Qdrant (ports 6333/6334) - **NOT required for alpha validation**
- **Future:** MemGraph/Neo4j for graph relationships (Month 6+)

**Hosting/Infrastructure:**
- **Alpha Phase:** Google Cloud Run (see `infra/` subdirectory for Tofu/Terraform config)
- **Local Dev:** Docker Compose with `make demo` command; can point to staging for testing
- **Secrets Management:** Environment variables via `.env` files (local) and Cloud Run secrets (production)

**Infrastructure Notes:**
- **Cloud Run Module:** Currently using Tofu built-in module (janky); upgrade to Cloud Run v2 post-alpha
- **Production Deployment:** Need to duplicate staging Tofu config → separate production environment with new Supabase config
- **Alpha Users:** May onboard to staging initially, then migrate to production once deployed

---

### Architecture Considerations

**Repository Structure:**
- **Monorepo:** Single repo at `/home/peleke/Documents/Projects/swae/MindMirror` containing all services, mobile app, web app
- **Service Isolation:** Each service has independent `pyproject.toml` (Poetry), migrations (Alembic), and GraphQL schema

**Service Architecture:**
- **Federated Microservices:** GraphQL Hive Gateway composes schemas from 7 independent services
- **Voucher Flow (Critical for Alpha):**
  1. **Web app** generates magic link with embedded voucher (handled by `web/` subdirectory voucher endpoint)
  2. User clicks link → **voucher mints** (email + program_id stored in Supabase database)
  3. User signs up via **Supabase Auth** → email matching validation
  4. User logs in → **auto-enrollment** triggered (GraphQL mutation: trace `autoenroll` in `practices_service`)
  5. **Mobile app** fetches assigned program via gateway → displays in UI
  6. User completes workout → **data persists** to Practices service database

**Integration Requirements:**
- **Authentication:** Supabase JWT tokens validated at gateway level, passed to services
- **GraphQL Federation:** Services must be healthy for gateway to compose supergraph (2-stage build: `mesh-compose` → `gateway`)
- **Admin Tooling Integration:** Extend existing `web/` admin UI (auth already configured; reuse existing habits/lessons magic link flow)
- **Email Rendering:** React-based email templates already exist via Supabase Edge Function; reusable for alpha invites

**Security/Compliance:**
- **Authentication:** Supabase handles user auth; JWT tokens passed to services via gateway
- **Authorization:** Services validate user context via `shared.auth.get_current_user()` dependency
- **Data Privacy:** Alpha users are known contacts (no GDPR concerns); workout data is non-sensitive
- **Test Data Isolation:** Use `test+alpha1@domain.com` email aliases for alpha testing

**Testing Requirements (CRITICAL for Alpha):**
- **Repeatability:** All testing workflows must be executable multiple times without manual database cleanup
- **Admin UI Vision:** Type email → button generates magic link + sends campaign-rendered email → click through full flow from single interface (ideal "first pass target")
- **Automation Path:** Admin UI must expose workflow that can eventually be scripted (Bash/Python)
- **Observability:** Enable verbose logging during alpha phase to capture edge cases (tail service logs via Docker Compose or Cloud Run)

---

## Constraints & Assumptions

### Constraints

**Budget:**
- **Zero ad spend during alpha** - No Facebook/Reddit ads, no paid user acquisition
- **Infrastructure costs:** Existing Cloud Run staging environment already deployed; production deployment adds minimal cost for 3 users
- **Tooling costs:** Existing stack (Supabase, Qdrant, PostgreSQL) already provisioned; no new subscriptions required
- **Development costs:** Solo developer/founder time only; no contractor/agency spend

**Timeline:**
- **Hard deadline:** Monday (Week 1 Day 5) for alpha invites - cannot slip without impacting Month 2-3 roadmap
- **Week 1 constraint:** 5 days (Wednesday→Sunday) to complete stress testing, bug fixes, program creation, and onboarding
- **Daily capacity:** ~5-7 hours/day available for focused work (realistic constraint, not optimistic)
- **Week 2-4 constraint:** Focus exclusively on alpha bug fixes; defer all parallel work (Stripe, PDFs) to avoid velocity risk

**Resources:**
- **Solo developer:** All engineering, product, and operations work done by single person
- **Known alpha users:** 3 users already identified and willing to participate; no backup users lined up
- **Existing infrastructure:** Must work within constraints of current architecture (federated GraphQL, Cloud Run, PostgreSQL); no time for major refactors
- **Admin tooling:** Must extend existing `web/` admin assets; cannot build standalone admin app from scratch

**Technical:**
- **No Celery/Redis for alpha:** Current architecture uses fire-and-forget synchronous service calls for reindexing; future transition to GCP Pub/Sub (not during alpha)
- **Cloud Run module upgrade deferred:** Currently using Tofu built-in Cloud Run module (janky); upgrade to Cloud Run v2 post-alpha
- **Staging→Production duplication needed:** Create separate production deployment (new Supabase config, better lockdown, performance tuning); alpha users may start on staging then migrate
- **Federated GraphQL dependency:** Gateway requires all services to be healthy for schema composition; service downtime blocks gateway startup
- **Local dev flexibility:** Docker Compose can point to staging databases/services for testing; acceptable for alpha but adds risk if staging breaks

---

### Key Assumptions

**Infrastructure Readiness:**
- ✅ Voucher flow for habits/lessons works reliably → auto-enroll mutation in practices_service has been tested and works
- ✅ Practices service GraphQL endpoints exist and are functional → only UI polish + bug fixes required
- ✅ Cloud Run staging environment is stable enough for 3 concurrent users → no scaling/performance issues expected (will find out if wrong)
- ✅ Existing admin assets in `web/` subdirectory are extendable → magic link generation UI can be built in ~2 hours by reusing habits/lessons flow
- ✅ Email rendering already works → React-based templates + Supabase Edge Function reusable for alpha invites
- ⚠️ **Risk:** If admin UI extension requires major refactor, could delay Week 1 timeline

**User Availability & Engagement:**
- ✅ All 3 alpha users will respond to invites and complete signup within 24-48 hours
- ✅ Users will tolerate rough edges (polish issues, confusing labels) if core functionality works ("just needs to work" threshold)
- ✅ Users will provide candid, actionable feedback when asked ("What sucked? What was confusing?")
- ✅ Users 1-2 have time for daily check-ins; User 3 has time for weekly check-ins
- ✅ 50% adherence rate is acceptable signal for alpha (repeated usage validates stickiness potential)
- ⚠️ **Risk:** If any user drops out or doesn't engage, 33% of alpha data is lost

**Development Velocity:**
- ✅ Critical bugs discovered in stress testing (Days 1-2) can be fixed within Day 3 timeline
- ✅ Programs for Users 2-3 can be created manually in app UI within 48-72 hours (Days 6-7)
- ✅ Admin UI for magic link generation can be built within ~2 hours (Day 1-2 parallel work)
- ✅ Week 2-4 bug fixes can be handled reactively (as users report issues) without blocking focus
- ✅ Test email accounts can be created quickly (`test+alpha1@domain.com` pattern)
- ⚠️ **Risk:** If Day 3 reveals infrastructure-level bugs (not just UI polish), could require multi-day fixes and delay invites

**Workout State Persistence:**
- ⚠️ **NEEDS INVESTIGATION:** Verify that navigating away from workout mid-session saves current state (duration elapsed, sets completed)
- ⚠️ **RISK:** If workout state doesn't persist, users lose trust when progress disappears
- ✅ **MITIGATION:** Add to Day 1-2 investigation checklist; if broken, prioritize fix in Day 3 critical bug phase

**Strategic Decision-Making:**
- ✅ 3 users across 4 weeks provides sufficient signal for Month 3-6 strategic direction (accept higher error margin for speed)
- ✅ Qualitative feedback (interviews, check-ins, enthusiasm) is as valuable as quantitative data (workout logs, adherence rates)
- ✅ Alpha results will clearly indicate which demographic to focus on; if truly mixed, default to combat sports and regroup
- ⚠️ **Risk:** If all 3 segments show weak signals, may require additional validation before committing to roadmap

**Post-Alpha Path:**
- ✅ If alpha succeeds, infrastructure is ready for beta testing (10-20 users) without major refactors
- ✅ Reddit/Facebook validation can begin immediately after alpha without waiting for additional polish
- ✅ Revenue infrastructure (Stripe, PDFs, email automation) can be built in Month 2 post-alpha
- ⚠️ **Risk:** If alpha reveals major infrastructure gaps, Month 2 timeline (beta + revenue) could slip by 2-4 weeks

---

## Risks & Open Questions

### Key Risks

**1. TECHNICAL RISK: Infrastructure Bugs Block Alpha Launch**
- **Description:** Stress testing (Days 1-2) reveals critical bugs in voucher flow that cannot be fixed within Day 3 timeline (e.g., enrollment logic broken, data loss on workout save, gateway composition failures)
- **Impact:** High - Would delay Monday alpha invites, potentially slipping entire Week 1 timeline by 2-4 days
- **Likelihood:** Low-Medium - Auto-enroll has been tested and works; most risk is in edge cases
- **Mitigation:**
  - Timebox Day 3 bug fixes to 6 hours; if not resolved, delay invites to Tuesday/Wednesday and adjust schedule
  - Prioritize "showstopper" bugs (crashes, data loss) over "polish" bugs (ugly UI) during Days 1-2 testing
  - Have rollback plan: Focus alpha on User 1 only if Users 2-3 programs aren't ready

**2. OPERATIONAL RISK: Admin UI Takes Longer Than Expected**
- **Description:** Extending `web/` admin assets for magic link generation requires more than ~2 hours (e.g., unexpected auth complications, missing API endpoints)
- **Impact:** Low - Delays streamlined testing workflow, but doesn't block alpha invites (can manually generate links via database/scripts as fallback)
- **Likelihood:** Low - Auth exists, habits/lessons flow is reusable, voucher endpoint already works
- **Mitigation:**
  - Build minimum viable admin UI first: input field for email + program ID → button generates link → display for copy/paste
  - If UI takes >4 hours, defer to Week 2 and use manual script-based magic link generation for Week 1
  - Document workflow during Day 1 investigation to clarify scope

**3. USER RISK: Alpha User Drops Out or Doesn't Engage**
- **Description:** One or more of the 3 alpha users doesn't respond to invite, fails to complete signup, or stops engaging after Week 1
- **Impact:** High - Loses 33% of alpha data per dropped user; weakens strategic decision-making signal
- **Likelihood:** Low-Medium - Users are known contacts, but life happens (injuries, schedule conflicts, tech frustrations)
- **Mitigation:**
  - Send invites with clear expectations ("Need 3 workouts/week for 4 weeks, will check in daily/weekly")
  - Over-communicate during Week 1: Daily check-ins for Users 1-2, proactive "How's it going?" outreach for User 3
  - If user drops in Week 1, accept 2-user alpha and adjust strategic decision framework accordingly

**4. STRATEGIC RISK: Weak or Mixed Signals from All 3 Segments**
- **Description:** Week 4 decision framework reveals no clear winner (e.g., all users show 40-60% adherence, mixed feedback, no strong "I'd pay for this" signals)
- **Impact:** Medium - Cannot confidently choose Month 3-6 demographic focus, may require additional validation
- **Likelihood:** Medium - 3 users is small sample; mixed results are plausible
- **Mitigation:**
  - Default to "gut feel" winner (likely combat sports) even if data is mixed—avoid analysis paralysis
  - If truly unclear, run mini-beta (10 users) of top 2 segments in Month 2 before full commitment
  - Pivot criteria: If all 3 segments weak, regroup and consider alternative wedge (nutrition-first, journaling-first)

**5. TECHNICAL RISK: Workout State Doesn't Persist on Navigation**
- **Description:** Users navigate away from workout mid-session (app backgrounded, screen locked, switched apps) and lose progress (sets completed, duration elapsed)
- **Impact:** High - Damages trust, creates frustration, drives drop-off
- **Likelihood:** Medium - Needs investigation; unclear if current implementation handles this
- **Mitigation:**
  - **PRIORITY INVESTIGATION (Day 1):** Trace workout logging flow in `practices_service` and mobile app to verify state persistence
  - If broken, prioritize fix in Day 3 critical bug phase (must save duration + completed sets on navigation events)
  - Acceptable: Rest timer resets on navigation (not critical); duration + sets must persist

**6. INFRASTRUCTURE RISK: Cloud Run Staging Instability**
- **Description:** Staging environment crashes, services fail to deploy, or database issues during alpha testing
- **Impact:** High - Blocks user access, damages trust, wastes alpha testing window
- **Likelihood:** Low - Staging has been running, but 3 concurrent users could expose edge cases
- **Mitigation:**
  - Monitor Cloud Run logs daily during Week 1 for error spikes
  - Accelerate production deployment if staging shows instability (may onboard users to production instead)
  - Have emergency rollback: Point local Docker Compose to production databases temporarily if staging fails

---

### Open Questions

**Infrastructure & Implementation (Day 1 Investigation):**

1. ✅ **RESOLVED:** Web admin auth is configured
2. ✅ **RESOLVED:** Magic link generation handled by voucher endpoint in `web/` subdirectory
3. ✅ **RESOLVED:** Auto-enroll mutation in practices_service works (tested)
4. ✅ **RESOLVED:** Email rendering uses React templates via Supabase Edge Function (reusable)
5. ❓ **Trace `autoenroll` mutation end-to-end:** Map full flow from voucher minting → user signup → auto-enrollment trigger → program assignment
6. ❓ **Admin UI scope clarification:** Does admin need to specify program ID explicitly, or can voucher system infer from service-agnostic configuration?
7. ❓ **Workout state persistence verification:** Does navigating away save duration + sets completed? Test and document behavior.
8. ❓ **Workout defer/shift API:** Confirm 1-day shift exists; determine if arbitrary shift (X days) requires extension
9. ❓ **Test email account setup:** Create `test+alpha1@domain.com`, `test+alpha2@domain.com`, `test+alpha3@domain.com` accounts

**User Experience & Product:**

10. ❓ **Pain/progress notes input placement:** Embed near "Complete Workout" button vs. separate journal card prompt post-workout?
11. ❓ **Skipped workout behavior:** If user doesn't complete workout, does schedule auto-advance or wait for manual shift?
12. ❓ **Mid-workout exit handling:** Can users restart workout from where they left off, or does it reset?
13. ❓ **Program progression (Week 3):** Manual phase advancement vs. auto-progression logic? Clarify for alpha expectations.

**Strategic & Process:**

14. ❓ **Week 4 decision rubric:** Engagement + enthusiasm are key, but formalize lightweight scoring if helpful
15. ✅ **RESOLVED:** If combat sports wins, recruit beta users from current gym + nearby gym with training partners
16. ✅ **RESOLVED:** If all segments weak, default to combat sports and regroup
17. ✅ **RESOLVED:** 50% adherence acceptable for alpha (repeated usage signal sufficient)

**Technical Debt & Future Work:**

18. ✅ **RESOLVED:** Cloud Run Tofu module upgrade (v2) deferred to post-alpha
19. ❓ **Production deployment timeline:** Create before alpha invites, or deploy mid-alpha if staging proves unstable?
20. ✅ **RESOLVED:** Pub/Sub migration deferred to Month 3-6+ (not relevant for alpha)
21. ✅ **RESOLVED:** Qdrant not needed for alpha validation (can ignore completely)

---

### Areas Needing Further Research

**1. Trace Auto-Enroll Mutation End-to-End (Day 1 Morning - 2 hours)**
- **Why:** Need to understand full voucher flow to build admin UI and validate stress testing approach
- **Investigation:**
  - Read `autoenroll` mutation in `practices_service` GraphQL schema
  - Trace voucher minting logic in `web/` subdirectory
  - Map database tables involved (vouchers, program_instances, user_enrollments)
  - Document end-to-end flow in testing checklist
- **Output:** Clear understanding of Steps 1-6 (magic link → auto-enrollment) to inform admin UI build

**2. Verify Workout State Persistence (Day 1 Afternoon - 1-2 hours)**
- **Why:** Critical UX issue—users will lose trust if progress disappears on navigation
- **Investigation:**
  - Test mobile app: Start workout → complete 2 sets → background app → reopen → verify state
  - Review `app/(app)/client/[id].tsx` workout UI code for cache persistence logic
  - Check `practices_service` API for "update workout progress" endpoint
  - Document current behavior (works / broken / partially broken)
- **Output:** Add to Day 3 critical bug list if broken; document expected behavior for alpha

**3. Admin UI Scope Definition (Day 1 Afternoon - 1 hour)**
- **Why:** Clarify whether admin needs program ID selection or can reuse existing habits/lessons flow
- **Investigation:**
  - Review existing magic link generation UI for habits/lessons in `web/` admin
  - Check if voucher endpoint accepts generic program_id or requires service-specific config
  - Determine if email template rendering is already integrated or needs adaptation
- **Output:** Technical spec for admin UI extension (input fields, API calls, workflow)

**4. Production Deployment Planning (Day 2 - 2-3 hours)**
- **Why:** Best practice to separate staging/production; alpha users may need production if staging unstable
- **Investigation:**
  - Duplicate `infra/` Tofu configuration for production environment
  - Create new Supabase project for production (separate from staging)
  - Document deployment steps and rollback procedures
  - Decide: Deploy before alpha invites, or deploy reactively if staging issues arise?
- **Output:** Production deployment runbook; decision on timing (pre-alpha vs. reactive)

**5. Workout Defer/Shift API Validation (Day 2 - 1 hour)**
- **Why:** Users may need to skip workouts (injury, schedule conflict); need to understand current capabilities
- **Investigation:**
  - Check `practices_service` API for defer/shift mutations
  - Test: Can user shift single workout by 1 day? By X days? Shift entire schedule?
  - Document limitations (e.g., only 1-day shifts supported)
- **Output:** Add API extension to backlog if arbitrary shifts needed; document workaround for alpha

---

## Next Steps

### Immediate Actions

1. **Day 1 Morning:** Trace `autoenroll` mutation end-to-end; verify workout state persistence; scope admin UI extension
2. **Day 1 Afternoon:** Build admin UI for magic link generation (target: ~2 hours); create test email accounts
3. **Day 2:** Execute 8 systematic stress test rounds; document all bugs with severity classification
4. **Day 3:** Fix all critical bugs; defer polish to Week 2; verify admin workflow takes <2 minutes
5. **Day 4:** Invite User 1 (knee rehab); monitor signup and first workout; fix urgent blockers
6. **Days 6-7:** Build programs for Users 2-3; send invites; confirm all users onboarded by Sunday
7. **Weeks 2-4:** Daily/weekly check-ins; reactive bug fixes; track adherence and feedback
8. **Week 4 End:** Analyze alpha data; document strategic decision (which demographic to focus Month 3-6)

---

## Appendices

### A. Research Summary

**Key Findings from Brainstorming Session (2025-10-15):**

- **Most systems are 70-90% built:** Focus is on hardening, testing, and validation—not new feature development
- **Validation before building:** Don't scale ads, don't finish PDF sales funnel until alpha proves infrastructure works
- **Users care about adaptivity, not tracking:** Optimize for "this adapts to YOU" messaging, not "tracking delight"
- **GitOps timing is critical but not urgent:** Need before scaling to dozens of users, but manual deployments fine for alpha
- **Revenue model doesn't depend on app success:** $20 PDF × 1,000/month = $20K MRR is profitable alone; app activation is bonus

**Alpha Validation Plan Highlights:**
- **Week 1 Strategy:** Stress test Steps 1-7 with test accounts (Days 1-2) → fix critical bugs (Day 3) → invite User 1 (Day 4) → monitor first workout (Day 5) → build/invite Users 2-3 (Days 6-7)
- **Decision Point (Week 4):** Analyze which demographic (rehab, postural, combat sports) shows strongest engagement signals to inform Month 3-6 roadmap
- **Red Flags (Stop and Fix):** Voucher system breaks, data doesn't save, app crashes mid-workout, magic links don't work

---

### B. References

- **Alpha Validation Plan:** `/home/peleke/Documents/Projects/swae/MindMirror/docs/alpha-validation-week-1.md`
- **Week 1 Execution Checklist:** `/home/peleke/Documents/Projects/swae/MindMirror/docs/week-1-execution-checklist.md`
- **Brainstorming Session Results:** `/home/peleke/Documents/Projects/swae/MindMirror/docs/brainstorming-session-results.md`
- **Infrastructure Config:** `/home/peleke/Documents/Projects/swae/MindMirror/infra/` (Cloud Run Tofu/Terraform)
- **Web Admin Assets:** `/home/peleke/Documents/Projects/swae/MindMirror/web/` (Next.js app with existing admin UI)
- **Mobile App Workout UI:** `/home/peleke/Documents/Projects/swae/MindMirror/mindmirror-mobile/app/(app)/client/[id].tsx`
- **Practices Service:** `/home/peleke/Documents/Projects/swae/MindMirror/practices_service/` (GraphQL schema, auto-enroll mutation)

---

### C. PM Handoff

This Project Brief provides the full context for **Swae OS Soft Launch** alpha validation. The brief defines a focused 4-week initiative to stress test voucher-based workout program infrastructure with 3 real users, validate product-market fit signals across distinct demographics, and establish strategic direction for Month 3-6 roadmap.

**Next Step:** Create a detailed Product Requirements Document (PRD) that translates this brief into actionable functional requirements, user stories, and acceptance criteria for implementation.

Please start in **PRD Generation Mode**, review this brief thoroughly, and work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.

---

**END OF PROJECT BRIEF**
