# Movements Service Migration Guide

## Issue: Missing `description` Column

The production database is missing the `description` column that the model expects.

## Quick Fix: SQL Direct Add (Recommended for Production)

```sql
-- Add missing description column
ALTER TABLE movements.movements
ADD COLUMN IF NOT EXISTS description VARCHAR;
```

This is safe to run and will have no effect if the column already exists.

## Full Migration Path (Using Alembic)

### 1. Check Current Migration Version

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/movements_service

# Set your database URL
export DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:6543/postgres"

# Check current version
poetry run alembic current
```

### 2. Run All Pending Migrations

```bash
# Run all migrations
poetry run alembic upgrade head

# Should apply:
# - 0001_init (if not already)
# - 0002_add_metadata_jsonb (if not already)
# - 0003_add_description_column (NEW)
```

### 3. Verify Migrations Applied

```bash
poetry run alembic current
# Should show: 0003_add_description_column (head)
```

## Verification SQL

After running the migration, verify the schema:

```sql
-- Check all columns
SELECT
  column_name,
  data_type,
  is_nullable,
  ordinal_position
FROM information_schema.columns
WHERE table_schema = 'movements'
  AND table_name = 'movements'
ORDER BY ordinal_position;

-- Should include:
-- ...
-- | description      | character varying | YES | ... |
-- | short_video_url  | character varying | YES | ... |
-- | long_video_url   | character varying | YES | ... |
-- | metadata         | jsonb            | YES | ... |
-- ...
```

## If Alembic Fails

If you can't use Alembic, just run the SQL directly:

```sql
-- Add description column (safe to run multiple times)
ALTER TABLE movements.movements
ADD COLUMN IF NOT EXISTS description VARCHAR;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'movements'
  AND table_name = 'movements'
  AND column_name = 'description';

-- Expected: description | character varying
```

## After Migration: Run Imports

Once the `description` column exists, you can run the imports:

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# ExerciseDB
poetry run python standalone_movements_import.py \
  "$PRODUCTION_DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# PN (Jen only)
poetry run python standalone_pn_import.py \
  "$PRODUCTION_DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv
```

## Troubleshooting

### "relation movements.alembic_version does not exist"

Alembic hasn't been initialized. Run:

```bash
# Initialize Alembic version table
poetry run alembic stamp head
```

### Port 6543 vs 5432

Supabase uses:
- **Port 6543**: Pooler (PgBouncer) - for many connections
- **Port 5432**: Direct connection - for migrations/schema changes

For Alembic migrations, use **port 5432** (direct connection):

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"
```

For imports (standalone scripts), **port 6543** is fine (pooler).

### Connection Timeout

If migrations timeout, increase timeout in `alembic.ini`:

```ini
[alembic]
# ... existing config ...
connect_args = {"timeout": 60}
```

Or use the SQL direct approach instead.
