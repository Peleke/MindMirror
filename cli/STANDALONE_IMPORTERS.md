# Standalone Data Importers

**NO CLI DEPENDENCIES - Just pure Python scripts.**

📖 **See `VIDEO_URL_HANDLING.md` for detailed explanation of video URL strategy**

## Recommended Import Order

**IMPORTANT**: Import in this order for best results:

1. ✅ **ExerciseDB first** (broad catalog with biomechanical data)
2. ✅ **PN second** (upgrades overlapping exercises with better videos)

This way, exercises that exist in both sources get PN's high-quality Vimeo videos + ExerciseDB's biomechanical attributes.

## Prerequisites

1. Get your database URLs from Supabase dashboard
2. Set environment variables OR pass directly to scripts

## Environment Setup

```bash
# For Staging
export STAGING_DB="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

# For Production
export PRODUCTION_DB="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"
```

## 1. PN Movements Import (Jen Only - RECOMMENDED)

**Note**: Jen's video becomes the PRIMARY `shortVideoUrl` shown in UI.

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Staging (Jen only)
poetry run python standalone_pn_import.py \
  "$STAGING_DB" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv

# Production (Jen only)
poetry run python standalone_pn_import.py \
  "$PRODUCTION_DB" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv
```

**Optional**: Include Craig's videos as alternate (`longVideoUrl`):
```bash
poetry run python standalone_pn_import.py \
  "$STAGING_DB" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/craig_export.csv
```

## 2. Exercise CSV Import (ExerciseDB Format)

```bash
# Staging
poetry run python standalone_movements_import.py \
  "$STAGING_DB" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# Production
poetry run python standalone_movements_import.py \
  "$PRODUCTION_DB" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv
```

**Note**: This importer handles the ExerciseDB CSV format with biomechanical data (muscle groups, movement patterns, etc.). It will skip the header rows and parse the data correctly.

## 3. Habits/Programs Import

```bash
# Staging
poetry run python standalone_habits_import.py \
  "$STAGING_DB" \
  /workspace/data/habits/programs/unfck-your-eating

# Production
poetry run python standalone_habits_import.py \
  "$PRODUCTION_DB" \
  /workspace/data/habits/programs/unfck-your-eating
```

## Pre-Flight SQL Checks

### Check if metadata column exists (for PN import):

```sql
SELECT
  table_schema,
  table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_schema = 'movements'
  AND table_name = 'movements'
  AND column_name = 'metadata';

-- Should return:
-- movements | movements | metadata | jsonb | YES
```

### Check full movements table structure:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'movements'
  AND table_name = 'movements'
ORDER BY ordinal_position;
```

### If metadata column is missing, run migration:

```bash
# From movements_service directory
cd /home/peleke/Documents/Projects/swae/MindMirror/movements_service

# Check current migration version
poetry run alembic current

# Run migrations
poetry run alembic upgrade head
```

## Troubleshooting

**Import fails with "No module named 'movements'"**
- Make sure you're running from the cli directory
- The scripts add the correct paths automatically

**Database connection fails**
- Verify your database URL format: `postgresql+asyncpg://user:pass@host:port/database`
- Check that Supabase allows connections from your IP
- For Supabase, use port 5432 and database name `postgres`

**CSV not found**
- Use absolute paths for CSV files
- Verify files exist: `ls -la /path/to/file.csv`

**Habits import fails with "No module named 'content_parser'"**
- The script adds the path automatically
- Make sure `/workspace/data/habits/programs/unfck-your-eating/program.yaml` exists

## Notes

- ✅ All imports are **truly idempotent** - safe to run multiple times
- ✅ Existing records are **updated**, not duplicated (matches by `slug` for movements)
- ✅ Handles duplicate slug errors gracefully with rollback
- ✅ Uses content hashing to detect changes (habits)
- ✅ Queries by unique constraint (`slug`) to prevent duplicates

## Quick Start - Complete Workflow

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Set your database URL
export DB_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

# Import in recommended order:

# 1. ExerciseDB (broad catalog)
poetry run python standalone_movements_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# 2. PN Movements (better videos - Jen only)
poetry run python standalone_pn_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv

# 3. Habits/Programs
poetry run python standalone_habits_import.py \
  "$DB_URL" \
  /workspace/data/habits/programs/unfck-your-eating
```

**Expected Results**:
- ~400+ exercises from ExerciseDB with biomechanical data + YouTube videos
- ~445 PN exercises with Vimeo videos
- Overlapping exercises (~355) have PN videos + ExerciseDB biomechanical data
- All habits/programs/lessons imported
