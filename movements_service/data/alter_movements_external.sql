-- Movements external integration (ExerciseDB) — apply in Supabase
-- Safe to run multiple times (IF NOT EXISTS / IF NOT EXISTS index)

-- 1) Add columns on base table for external linkage and rich attributes
ALTER TABLE movements.movements
  ADD COLUMN IF NOT EXISTS external_source TEXT,
  ADD COLUMN IF NOT EXISTS external_id TEXT,
  ADD COLUMN IF NOT EXISTS image_url TEXT,
  ADD COLUMN IF NOT EXISTS video_url TEXT,
  ADD COLUMN IF NOT EXISTS exercise_type TEXT,
  ADD COLUMN IF NOT EXISTS body_parts TEXT[],
  ADD COLUMN IF NOT EXISTS equipments TEXT[],
  ADD COLUMN IF NOT EXISTS target_muscles TEXT[],
  ADD COLUMN IF NOT EXISTS secondary_muscles TEXT[],
  ADD COLUMN IF NOT EXISTS keywords TEXT[],
  ADD COLUMN IF NOT EXISTS overview TEXT,
  ADD COLUMN IF NOT EXISTS instructions JSONB,
  ADD COLUMN IF NOT EXISTS exercise_tips JSONB,
  ADD COLUMN IF NOT EXISTS variations JSONB,
  ADD COLUMN IF NOT EXISTS related_external_ids TEXT[],
  ADD COLUMN IF NOT EXISTS metadata JSONB;

-- 2) Idempotent unique index on (external_source, external_id)
CREATE UNIQUE INDEX IF NOT EXISTS movements_external_source_id_uidx
  ON movements.movements (external_source, external_id)
  WHERE external_source IS NOT NULL AND external_id IS NOT NULL;

-- 3) Optional performance indexes (comment out if undesired)
-- CREATE INDEX IF NOT EXISTS movements_name_trgm_idx ON movements.movements USING gin (name gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS movements_slug_trgm_idx ON movements.movements USING gin (slug gin_trgm_ops);
-- CREATE INDEX IF NOT EXISTS movements_keywords_gin_idx ON movements.movements USING gin (keywords);

-- 4) Notes
-- - The service ORM currently persists instructions via a separate table (movement_instructions).
--   The JSONB instructions field is provided for flexibility or future migrations.
-- - image_url/video_url are optional; service currently uses gif_url/short_video_url/long_video_url.
--   Keeping these columns enables richer external data retention without schema churn. 