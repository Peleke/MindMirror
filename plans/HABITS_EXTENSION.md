### Habits Extension: Daily Variants and Journal Prompts

Goal: Make programs feel “alive” by allowing a step’s primary habit to feature a small daily variant (“sub-habit”) and a coordinated daily journal prompt, while preserving the main habit identity and keeping content operations simple.

Principles
- Keep the main habit stable (e.g., Eat Slowly) while enabling a per-day nudge (variant) that changes flavor/angle.
- Journal prompts align with the habit for the same day.
- Start with a manual-friendly workflow. Automate parsing later.

Data Model
- New table: `step_daily_plan`
  - `id` (UUID PK)
  - `program_step_template_id` (FK)
  - `day_index` (int, 0-based within the step)
  - `habit_variant_text` (text, nullable)
  - `journal_prompt_text` (text, nullable)
  - `lesson_segment_id` (UUID, nullable) — optional link to a “lesson segment” if long lessons are split across days
  - `metadata_json` (jsonb, nullable)
  - Unique: (`program_step_template_id`, `day_index`)

- Optional new table: `lesson_segments`
  - `id` (UUID PK)
  - `lesson_template_id` (FK)
  - `day_index_within_step` (int) — or explicit mapping via `step_daily_plan`
  - `title`, `subtitle`, `markdown_content`, `summary`

Planner Changes
- For the active step/day:
  - If `step_daily_plan.habit_variant_text` exists, surface it as `subtitle` on the HabitTask (overriding default fallback logic).
  - If journaling program is assigned, create/add a `JournalTask` with `title` (e.g., “Daily Journal”) and `description` set to `journal_prompt_text`. If journaling program is not enrolled, show the prompt in habit detail instead.
  - If `lesson_segment_id` is present, surface that segment as the day’s lesson instead of the full lesson (back-compat if segments don’t exist).

GraphQL
- Query: `programStepDailyPlan(programStepId: String!)` → array of `{ dayIndex, habitVariantText, journalPromptText }`.
- Extend `todaysTasks(onDate)` to include `subtitle` populated from daily plan when available.
- Step detail can render the full week’s variants/prompts for preview.

Seeding & Content Ops
- Phase 1 (manual-friendly): allow a sidecar YAML (`step.yaml`) alongside `program.yaml` with structure:
  ```yaml
  daily_plan:
    - day_index: 0
      habit_variant_text: "Put the phone in another room during dinner"
      journal_prompt_text: "What changed when screens were away?"
    - day_index: 1
      habit_variant_text: "Use grayscale mode after 8pm"
      journal_prompt_text: "How did grayscale affect impulse scrolling?"
  ```
- Phase 2: parsing from lesson markdown blocks (e.g., frontmatter sections) to auto-fill daily plan.
- Phase 3: optional `lesson_segments` creation by splitting long lessons into daily chunks.

Mobile UI
- Home: Habit card uses `subtitle` (daily variant) automatically. Journal task shows prompt (if journaling assignment exists).
- Step detail: show a “This week’s plan” accordion listing variants/prompts by day.
- Lesson detail: if segments exist, show only today’s segment; otherwise show full lesson (back-compat).

Back-compat and Rollout
- If no `step_daily_plan` rows or no segments exist, behavior remains as now.
- Start with 1–2 programs (e.g., Unf*ck Your Eating, Daily Journaling) to validate content ops.

Future Enhancements
- A/B test daily variants (two prompts for a day; randomized), track adherence and reflection quality.
- Authoring UI (internal) for editors to manage daily plans and preview timelines.

### Lesson Segmentation Options (splitting long lessons into daily chunks)

Authoring constraints: content lives in `data/habits/programs/<program>/` as markdown files with frontmatter. We want segmentation that is simple, minimizes parser magic, and is friendly to authors.

Recommended options (prefer in this order):

1) Sidecar YAML map (no markdown surgery; simplest ops)
  - Keep the canonical lesson markdown intact.
  - Add a `segments.yaml` alongside the lesson (or `step.yaml` for the step) with entries that reference slice boundaries and override titles/subtitles when needed.
  - Example (`005_lesson.md` sits next to `005_segments.yaml`):
    ```yaml
    segments:
      - day_index: 0
        title: "Screens Off: Setup"
        subtitle: "Create your environment"
        extract: {
          type: "heading_range",
          from: "## Why screens off",
          to: "## Practice"
        }
      - day_index: 1
        title: "Screens Off: Practice"
        extract: { type: "heading", match: "## Practice" }
    ```
  - Seeder resolves references and persists `lesson_segments` rows; planner surfaces per-day segment.
  - Upside: clear author intent, no ambiguous parsing; downside: one more file.

2) Multiple markdown files per logical lesson
  - Author `005_day0.md`, `005_day1.md`, etc., each with frontmatter linking back to the parent lesson slug/id.
  - Seeder groups them under a single parent or stores as child segments.
  - Upside: maximal clarity; downside: more files to manage.

3) Frontmatter sections within a single markdown
  - Use structured frontmatter to declare segments and anchors:
    ```yaml
    segments:
      - day_index: 0
        anchor: "## Part 1"
      - day_index: 1
        anchor: "## Part 2"
    ```
  - Seeder parses anchors and slices content. Requires stable headings.

4) Pure markdown heading parsing (least preferred)
  - Infer segments by headings alone. Fast but brittle; authors must follow strict conventions.

Storage model
- Persist `lesson_segments` with a `parent_lesson_template_id`, `day_index_within_step`, `title`, `subtitle`, `markdown_content`, `summary`.
- Optionally keep `source_locator` for traceability (file + line ranges) to help editors.

Rendering
- Step detail/lesson detail fetches the segment for the specific day; if absent, falls back to the full lesson.
- Programs & Resources list can show segment titles as sub-items under a lesson (optional).

### Reusable Content Assets (e.g., protein add-in table) and Includes

Problem: Some lessons contain reusable artifacts (tables, short guides). We want them as standalone assets that can be linked/embedded across lessons, searchable, and referenceable by the assistant.

Design
- New table: `content_assets`
  - `id` (UUID), `slug` (unique), `title`, `subtitle?`, `content_markdown`, `type` (table|guide|tip), `tags` (json), `metadata_json` (json), timestamps.
- Join table: `lesson_assets` (many-to-many), optional `program_assets` if needed.
- Authoring:
  - Place assets in `data/assets/` as markdown with frontmatter:
    ```yaml
    slug: protein-addins
    title: Protein Add-in Guide
    type: table
    tags: [nutrition, protein]
    ```
  - Lessons reference assets via frontmatter or inline include directives (e.g., `{{ include: protein-addins }}`) that the renderer/CLI resolves to links or inlined content.

GraphQL and UI
- Queries: `contentAssets(filter)`, `contentAsset(slug)`, and on lesson: `assets` array.
- Programs & Resources: add an "Assets" filter to browse/search assets; open an asset detail page with share/download.
- Assistant: assets are independently indexed in Qdrant with `type`, `tags`, and usage metadata; the assistant can link a card or offer a PDF export.

Rendering strategy
- Default: render a link card to the asset in lesson detail (fast, keeps lessons slim), with an “open” action.
- Optional inline: for web/PDF export, expand the include inline (server-side rendering path) while keeping mobile lightweight.

Authoring ergonomics
- Keep includes declarative and minimal: `{{ include: slug }}`. CLI validates slugs exist.
- Provide a preview CLI command to show how includes resolve and segments slice.



