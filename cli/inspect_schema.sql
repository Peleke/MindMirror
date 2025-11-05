-- Inspect movements table schema in production

-- 1. Check all columns in movements table
SELECT
  column_name,
  data_type,
  character_maximum_length,
  is_nullable,
  column_default,
  ordinal_position
FROM information_schema.columns
WHERE table_schema = 'movements'
  AND table_name = 'movements'
ORDER BY ordinal_position;

-- 2. Check what migrations have been run
SELECT * FROM movements.alembic_version;
