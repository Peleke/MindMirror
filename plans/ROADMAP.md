### MindMirror Roadmap

This roadmap prioritizes a web-first acquisition funnel with native mobile for daily execution, tightening the loop between habit formation, journaling, and AI personalization. Each phase starts with the product case (why it matters), followed by actionable, itemized work.

### Immediate (1–2 weeks)
Product case: Land a polished demo and initial onboard that showcases both “wow” (animated insights + personalization) and core reliability (daily tasks flow that updates instantly). This validates the platform loop: enroll → do daily → see value → keep going.

- Core polish and stability
  - Ensure GraphQL Mesh and services expose new fields consistently (e.g., `subtitle`, `heroImageUrl`, `habitStats`, step progress) and are rebuilt on schema changes.
  - Fix GraphQL alias conflicts in `journalEntriesForHabit` by aliasing union member `payload` fields.
  - Add lightweight caching headers or `network-only` fetches on critical flows to prevent stale UI.

- Habit and lesson UX improvements
  - Home screen: show habit `subtitle` reliably (done; planner falls back to lesson subtitle/summary, then title). Keep.
  - Program detail: show step progress (started, daysCompleted/totalDays) and lesson previews per step (done). Keep.
  - Step detail: header above stats, then lessons, then linked entries (done). Keep.
  - Marketplace and Programs & Resources: show `subtitle` on cards (done). Keep.
  - “Daily Journaling” as ongoing program with daily card (done via assignment). Verify seed and enrollment paths.

- Habit stats on home (visual candy + motivation)
  - Add a compact adherence widget above gratitude/reflection in `/journal` using `habitStats` for current-most step habit.
  - Show current streak and completed/presented counts; use `react-native-svg` with simple animation.

- Qdrant indexing (journal + lessons for RAG)
  - Repair existing indexing for journal entries (including `habit_template_id` metadata and embeddings version tag).
  - Index lesson templates (title, subtitle, summary, outline) with `program_template_id` and `habit_template_id` link metadata.
  - Expose a consistent retrieval interface that includes “isHabitLinked” flags for entries.

- Optional: Switch to Pub/Sub for indexing triggers
  - Flip journal ingestion + habit/lesson content seeding to publish indexing messages to topics (already scaffolded), consume in `agent_service` indexer worker.
  - Validate idempotency and DLQ behavior.

- Deployment and DX
  - CI: build-and-push images for `habits_service`, `journal_service`, `agent_service`, CLI; run tests in CI.
  - Cloud Run deploy via Terraform/Tofu for services + Qdrant. Parameterize env via secrets.
  - Temporary startup `ALTER TABLE` guards retained; plan Alembic cutover queued in Near term.

(Assistant suggestion) Add a “What changed today” recap strip on home pulling recent completions and affirmations to immediately prove value after actions.

### Near (2–6 weeks)
Product case: Expand value pillars (nutrition + fitness) with unified enrollment and daily flows, deepening stickiness while keeping onboarding simple. Prepare foundations for scale (migrations, gateway auth, content ops).

- Movements graph visualization (browser-first; mobile-ready)
  - Build a React + D3.js (or Sigma.js) web explorer to visualize the `movements` graph: exercise node + connected muscles, patterns, planes, equipment, regressions/progressions, contraindications.
  - API: add endpoints to `movements` service for neighborhood queries (by id/slug), typed expansions, search, and short paths for substitutions.
  - UX: node focus, type filters, edge legends; click-through from practice UI to open explorer; shareable deep links.
  - Mobile reuse: architect graph layout components to be portable (React Native SVG path), so we can embed a simplified watcher in-app later.
  - PR value: host a read-only public version to showcase the knowledge graph (no auth), limited to non-proprietary data.

- Daily habit variation + journal prompt scheduling (make programs feel “alive”)
  - Goal: Each step’s primary habit can have a small daily variant ("sub-habit"/task) and a matching daily journal prompt (Mon–Sat) while keeping the main habit identity intact.
  - Data model (lightweight): introduce `step_daily_plan` mapping per dayIndex with fields: `habitVariantText`, `journalPromptText`, `lessonSegmentId?` (optional link to a lesson segment if content is split), `metadataJson`.
  - Planner: for the active step/day, surface `habitVariantText` on the HabitTask as `subtitle`/`description` override, and expose a `JournalTask` that uses `journalPromptText` when the user is assigned to a journaling program; otherwise attach prompt to habit detail.
  - GraphQL: add `programStepDailyPlan(programStepId)` and include `habitVariantText`/`journalPromptText` in `todaysTasks` response when available.
  - Seeding/content: extend CLI to parse lesson markdown or sidecar YAML (`step.yaml`) to extract daily variants and prompts; optionally split long lessons into per-day segments (manual-friendly). Keep a manual path first; add parsing later.
  - Back-compat: if no `step_daily_plan` rows exist, planner behavior remains unchanged.
  - See `plans/HABITS_EXTENSION.md` for details.

- Integrate `meals` service
  - Infra: add to Compose and Terraform/Tofu; provision DB; wire into Mesh (schema stitching/federation if needed).
  - Mobile UI: basic meal timeline + add/edit meal; minimal journaling link for context; daily calories/macros summary.
  - Later: CV-assisted estimation (deferred), but design API surface now to avoid refactors.

- Integrate `practices` (workouts)
  - Reuse patterns from habits: programs, enrollment, steps (workout blocks), daily tasks (workout-of-the-day), completion events.
  - Federation with `movements` graph service at the gateway to power exercise taxonomy (variants, progressions).
  - Mobile UI: Workout of Day, Program Detail (with step progress), Workout Detail (sets/reps tracking), History.
  - Implementation approach: review existing Flutter code and backend behavior, then reimplement the client UX from scratch in React Native as a first-class MindMirror experience, using the Flutter app as a reference (not target).

- Enrollment flows (B/C)
  - Flow B: auto-enroll based on email entitlements on login; surface safe retry semantics.
  - Flow C: code redemption (simple form, toast feedback, immediate task refresh).
  - Flow A (webhook/payments) deferred; keep provider-agnostic `entitlements` contract.

- RAG extension (habits + lessons + journals)
  - Agent retrieval composes: current/recent habits, step lessons, recent completions, linked journals.
  - Extend `customAffirmation` to include habits + lessons context (done in plan) and ship the PoC.

- Assessments service (short-term insert)
  - Introduce an `assessments` microservice for intake and periodic check-ins (e.g., weight, mood, readiness, goals) that attach to programs.
  - GraphQL: create assessment templates, assign to user on program enrollment (Prelude/Intake), record responses, list recent assessments.
  - Use assessment signals to enrich RAG context and inform planner (e.g., adjust habit emphasis based on readiness score).

- Content and migrations
  - Alembic migrations replacing startup `ALTER TABLE` guards; create base migration reflecting current schema.
  - Seeder: add “seed all programs in directory” mode; report version bumps and structural changes.

- Security and interservice calls
  - Implement HMAC-signed requests across services now (minimal), with a plan to move to interservice JWT later.
  - Start `users` service design for internal ID brokering (see Medium).

(Assistant suggestion) Add light-touch email digests (weekly recap: adherence, streaks, top journal themes) to drive retention; can be generated from existing stats and RAG summaries.

### Medium (6–16 weeks)
Product case: Transform from multi-feature app into a cohesive assistant-powered platform that adapts content and actions across habits, meals, workouts, and sleep. Strengthen the infra (auth, observability, reliability) to support growth.

- Assistant via tools (MCP over GQL)
  - Expose safe, parameterized tools for: enroll in program, mark habit response, complete lesson, log meal, start workout, add journal entry.
  - Agent planning layer that sequences multi-step flows (“Adjust today’s workout based on how I feel”).
  - Guardrails + audit for tool use.

- Observability and reliability
  - Jaeger/Honeycomb tracing across services via OpenTelemetry; trace sampling for high-traffic endpoints.
  - Error budgets + SLOs on core flows (todaysTasks, recordHabitResponse, markLessonCompleted, journaling mutations).
  - Synthetic checks for Mesh schema health.

- Sleep integration (Apple Health / Fitbit)
  - Ingest summaries (duration, efficiency, wake episodes), derive a daily readiness score.
  - Use in planner to adapt task emphasis (e.g., lighter workout; mindfulness habit) and in `customAffirmation`.

- Security and identity
  - `users` service for internal ID ↔ Supabase ID resolution; gateway injects `x-internal-id`.
  - Transition from HMAC to interservice JWT (short-lived, mTLS optional), rotate via secret manager.

- RAG scale and quality
  - Qdrant sharding and payload schema versioning; background re-index pipeline.
  - Hybrid retrieval (keyword + vector) with re-ranking for better recency and diversity.
  - Expand to meals/workouts/sleep entities with normalized metadata.

- Product growth surface
  - Public web mini-experiences (lesson previews, habit samplers) to drive enrollments.
  - Referral codes and lightweight community features (e.g., streak shoutouts).

(Assistant suggestion) Add a simple “coach handoff” export: compile last 7–14 days of habit adherence, workouts, and key journal themes into a shareable PDF—useful for paid upsells and coach onboarding.

### Execution notes
- Continue “dev-guarded mocks” for mobile while wiring live GraphQL to keep UI velocity high.
- Keep tests close to schema and planner logic; every new query/mutation should have integration coverage.
- Revisit design polish after stability: consistent card elevations/gradients, iconography system, and motion.

### Movements Graph Enrichment (planning note)
Product case: Enable intelligent workout adaptations without relying on GenAI by enriching the `movements` graph with rich semantics that support deterministic queries.

- Source reference (column mapping): The exercise metadata columns we’ll ingest (and keep in sync) are based on the spreadsheet structure here: [Functional Fitness Exercise Database v2.9](https://docs.google.com/spreadsheets/d/1zMYUkfVuTkHn08iiC5KoDcMnN8hps987pJr2_2iWnGo/edit?gid=2027036950#gid=2027036950).

- Graph data model (nodes, rels, properties)
  - Node types
    - Exercise: { slug, name, difficulty, shortVideoUrl, longVideoUrl, bodyRegion, forceType, mechanics, laterality, primaryClassification }
    - Muscle: { name, group } — e.g., Rectus Abdominis (group: Abdominals)
    - Joint: { name } — e.g., Shoulder, Knee
    - Equipment: { name }
    - Posture: { name } — e.g., Supine, Bridge, Quadruped, Seated Floor
    - ArmMode: { name } — e.g., Single Arm, Double Arm, No Arms
    - ArmPattern: { name } — e.g., Continuous, Alternating
    - Grip: { name } — e.g., Neutral, Pronated, Flat Palm
    - LoadPosition: { name } — e.g., Overhead, Hip Crease, No Load
    - LegPattern: { name } — e.g., Continuous, Alternating
    - FootElevation: { name } — e.g., Feet Elevated, No Elevation
    - ComboType: { name } — e.g., Single Exercise, Combination Exercise
    - MovementPattern: { name } — e.g., Hip Hinge, Knee Dominant, Vertical Push, Anti-Extension, Anti-Rotation
    - PlaneOfMotion: { name } — e.g., Sagittal, Frontal, Transverse
    - Contraindication: { name } — e.g., Knee Pain, Shoulder Impingement
    - Tag: { name }
  - Relationships
    - (Exercise)-[:TARGETS_PRIMARY]->(Muscle)
    - (Exercise)-[:TARGETS_SECONDARY]->(Muscle)
    - (Exercise)-[:TARGETS_TERTIARY]->(Muscle)
    - (Exercise)-[:INVOLVES]->(Joint)
    - (Exercise)-[:REQUIRES_PRIMARY {count}]->(Equipment)
    - (Exercise)-[:REQUIRES_SECONDARY {count}]->(Equipment)
    - (Exercise)-[:HAS_POSTURE]->(Posture)
    - (Exercise)-[:ARM_MODE]->(ArmMode)
    - (Exercise)-[:ARM_PATTERN]->(ArmPattern)
    - (Exercise)-[:GRIP]->(Grip)
    - (Exercise)-[:LOAD_POSITION]->(LoadPosition)
    - (Exercise)-[:LEG_PATTERN]->(LegPattern)
    - (Exercise)-[:FOOT_ELEVATION]->(FootElevation)
    - (Exercise)-[:COMBO_TYPE]->(ComboType)
    - (Exercise)-[:HAS_PATTERN]->(MovementPattern) — up to 3
    - (Exercise)-[:IN_PLANE]->(PlaneOfMotion) — up to 3
    - (Exercise)-[:HAS_TAG]->(Tag)
    - (Exercise)-[:PROGRESSES_TO]->(Exercise)
    - (Exercise)-[:REGRESSES_TO]->(Exercise)
    - (Exercise)-[:CONTRAINDICATED_FOR]->(Contraindication)
    - (Exercise)-[:VARIANT_OF]->(Exercise)
  - Exercise properties capture columns like difficulty, bodyRegion, forceType, mechanics (Compound/Isolation), laterality (Bilateral/Unilateral/Contralateral), primaryClassification (e.g., Bodybuilding, Postural), plus media links.

- Ingestion/seeding
  - Build a loader that maps spreadsheet columns to graph nodes/rels with controlled vocabularies (normalize values like posture, patterns, planes).
  - Validate counts (# primary/secondary items) on equipment rels; default to 0 when blank.
  - Keep a provenance record per Exercise node (source row id/timestamp) for re-imports.

- Queries to support
  - “Give regressions for Barbell Back Squat suitable for knee pain.”
    - Cypher (sketch):
      ```
      MATCH (e:Exercise {slug:$slug})-[:REGRESSES_TO]->(r:Exercise)
      WHERE NOT (r)-[:CONTRAINDICATED_FOR]->(:Contraindication {name:'Knee Pain'})
      RETURN r ORDER BY r.difficulty ASC LIMIT 10
      ```
  - “List progressions from supported movements for an intermediate lifter with limited shoulder mobility.”
    - Cypher (sketch):
      ```
      MATCH (e:Exercise {slug:$slug})-[:PROGRESSES_TO]->(p:Exercise)
      WHERE p.difficulty IN ['Intermediate','Advanced']
        AND NOT (p)-[:INVOLVES]->(:Joint {name:'Shoulder'})-[:HAS_LIMITATION]->(:Constraint {name:'Limited Mobility'})
      RETURN p ORDER BY p.difficulty ASC LIMIT 10
      ```
  - “Build a warmup for a Pull day with elbow pain (tissue prep + activation).”
    - Cypher (sketch):
      ```
      MATCH (mp:MovementPattern {name:'Pull'})<-[:HAS_PATTERN]-(e:Exercise)
      MATCH (warm:Tag {name:'Warmup'})
      WHERE NOT (e)-[:CONTRAINDICATED_FOR]->(:Contraindication {name:'Elbow Pain'})
      RETURN e ORDER BY e.difficulty ASC LIMIT 8
      ```
  - “Swap any movement requiring a barbell for dumbbells.”
    - Cypher (sketch):
      ```
      MATCH (e:Exercise)-[r:REQUIRES_PRIMARY]->(eq:Equipment {name:'Barbell'})
      WITH e
      MATCH (alt:Exercise)-[:HAS_PATTERN]->(:MovementPattern)<-[:HAS_PATTERN]-(e)
      WHERE (alt)-[:REQUIRES_PRIMARY]->(:Equipment {name:'Dumbbell'})
      RETURN DISTINCT alt LIMIT 10
      ```

- Integration with practices
  - Practices service queries movements graph at the gateway for substitutions and warmup generation.
  - Planner chooses safe substitutions automatically when user profile flags constraints.
  - UI: modification sheet shows rationale and alternatives.

### Go-to-Market & Growth Targets
Product case: Use a high-clarity wedge (UYE) to prove value fast, then expand with journaling, meals, and movement; compounding personalization drives retention and monetization.

- Where value is strongest
  - Daily behavior-change loop: Habit programs + journaling + AI personalization + streaks
  - Flagship wedge: UYE → immediate wins; then Daily Journaling, Movement, Meals
  - Cross-vertical compounding: data unlocks anticipatory interventions

- Close the gap quickly
  - Ship demo funnel: Landing → PDF+Sheet lead magnet → auto-enroll UYE → daily drips → stats & affirmations
  - Instant “aha”: adherence ring, streak potential, and a personalized affirmation on Day 1
  - Reduce friction: one-tap enroll, fast backnav, network-only refreshes after actions
  - Retention nudges: streak-saving push, weekly recap email with visuals
  - Content ops lite: daily variants + prompts + reusable assets; preview/validation/seed
  - Social proof & UGC: short testimonials, 7-day challenges with CTAs

- Targets by phase
  - Immediate (2–4 weeks)
    - Aggressive: 5–8k emails, 1–2k installs, 40–50% enroll; D7 30–35%; 10–15% WAU
    - Realistic: 1–2k emails, 300–600 installs, 25–35% enroll; D7 20–25%; 8–10% WAU
    - North-star: ≥60% complete ≥1 task on Day 1
  - Near (2–6 weeks)
    - Aggressive: 15–20k emails, 3–5k installs, 20–25% WAU/MAU; D30 18–22%; 3–5% paid trial opt-in
    - Realistic: 6–10k emails, 1.2–2.5k installs, 15–18% WAU/MAU; D30 12–15%; 1.5–3% paid
    - North-star: ≥4 completions/week; cross-enrollment by week 3
  - Medium (6–16 weeks)
    - Aggressive: 35–50k emails, 7–10k MAU; D90 15–18%; paid 5–7%
    - Realistic: 15–25k emails, 3–5k MAU; D90 10–12%; paid 3–4%
    - North-star: anticipatory nudges accepted ≥25%
  - Long-term (16–24 weeks)
    - Aggressive: 80–120k emails, 15–20k MAU; paid 7–9%; referrals ≥15%
    - Realistic: 35–60k emails, 7–12k MAU; paid 4–6%; referrals 8–10%
    - North-star: time-to-value < 1 minute/session

### Long-Term (16–24 weeks)
Product case: Deliver automated, anticipatory interventions and a premium, distinctive brand experience. The app should not only reflect the user’s data but proactively coach—suggesting habit adjustments, adapting workouts, and shaping affirmations and lessons to their current context. Pair with a top-tier design overhaul to differentiate.

- Automated anticipatory personalization
  - Daily planning layer consumes: recent journal semantics, habit adherence/streaks, workout progression, meal adherence, sleep readiness.
  - Generate proactive suggestions: “Slept poorly—shift to a lighter workout; add a reflection exercise after lunch,” with one-tap accept/modify/dismiss.
  - Push notifications: respectful windows, opt-in categories (habits, workouts, meals), smart batching to avoid fatigue.
  - Authorization model: small, explicit permissions for the agent to execute auto-adjustments (e.g., reschedule lesson, move workout) once accepted.
  - Feedback loop: when users accept/decline, log the rationale (if provided) and tune suggestion thresholds.

- Assistant maturity
  - Multi-goal orchestration: combine tools across services (“Hydration push + lighter workout + gratitude cue”).
  - Context memory: recent user choices and outcomes inform future suggestions; store in a compact “behavior summary”.
  - Safety: constrain long-running or stateful tool runs, add rollbacks for task updates.

- Design and branding overhaul (first-class)
  - Visual identity: color, typography, and component library refresh.
  - Motion language: Rive/Lottie-first microinteractions (enroll transitions, task completion confetti, adherence rings) with a unified animation system.
  - High-touch screens: marketplace, program detail, and home redesigned with expressive, animated components.
  - Performance budget: measure motion cost, pre-render critical art, and lazy-load assets.

- Platform integration and quality
  - Expand sleep integrations (Fitbit/Garmin/Apple Health); add HRV/readiness when available.
  - Personalization controls: a page where users set goals, preferred cadence, and intervention aggressiveness.
  - Reliability: graceful offline for daily tasks; sync on reconnect; clear conflict resolution for event writes.

- Example user flows (impact illustrations)
  - Morning nudge: “You slept 5h. Let’s do a calming mobility block and shift your intense workout to tomorrow? [Yes / Edit / No]” → auto-moves workout; streak remains; affirmation adapts.
  - Midday habit pivot: Journal trend shows stress—suggests a 2-minute breathing habit today; adds a quick reflection prompt and moves lesson to evening.
  - Nutrition assist: Meal logs show low protein—agent suggests a simple target for dinner; preloads an educational lesson.
  - Weekly review: A delightful animated recap with adherence ring growth, best streak, top journal theme, and a “next week focus” suggestion.
  - Coach mode: User exports a 14-day PDF for a trainer—workouts, adherence, notes—built in one tap.

(Assistant suggestion) Launch a small “intervention lab” feature flag: test new proactive strategies on a subset of users and measure accept/dismiss rates and downstream adherence.


