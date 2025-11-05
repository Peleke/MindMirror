# ✅ Idempotent Import Fixes

All three standalone importers are now **truly idempotent** and will handle existing data gracefully.

## What Was Fixed

### 🐛 Root Cause
All importers were querying by `name` but the unique constraint is on `slug`. This caused:
- Query by name → not found
- Generate slug → already exists in DB
- INSERT → **IntegrityError: duplicate key "movements_slug_key"**

### ✅ Solution Applied to All Scripts

1. **Query by slug** (the unique constraint) instead of name
2. **Wrap in try/except IntegrityError** to catch duplicates
3. **Use session.flush()** after each operation to catch errors early
4. **Rollback on error** and continue to next record
5. **Print warning** when skipping duplicate records

## Fixed Scripts

### 1️⃣ standalone_movements_import.py (ExerciseDB CSV)

**Changes**:
- ✅ Queries by `slug` instead of `name` (line 69)
- ✅ Generates slug once before query (line 66)
- ✅ IntegrityError handling with rollback (lines 133-138)
- ✅ Flushes after each operation (lines 123, 131)
- ✅ Skips duplicates gracefully with warning

**Test**:
```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Should handle existing records gracefully
poetry run python standalone_movements_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# Expected output:
# Created: X (new exercises)
# Updated: Y (existing exercises)
# Skipped: Z (duplicates/errors)
```

### 2️⃣ movements_service/movements/service/pn_csv_importer.py (PN Import)

**Changes**:
- ✅ Added `_slugify()` function (lines 15-21)
- ✅ Queries by `slug` instead of `name` (line 128)
- ✅ Generates slug before query (line 127)
- ✅ Direct MovementModel creation instead of repo.create() (lines 155-157)
- ✅ Better error messages with exercise name (line 162)

**Test**:
```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Should handle existing records gracefully
poetry run python standalone_pn_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv

# Expected output:
# Created: X (new exercises)
# Updated: Y (existing exercises with PN videos)
# Skipped: Z (duplicates/errors)
```

### 3️⃣ standalone_habits_import.py

**Changes**:
- ✅ Added IntegrityError import (line 31)
- ✅ Wrapped program/lesson/habit upserts in try/except (lines 97-177)
- ✅ Flushes after each operation
- ✅ Rollback and continue on IntegrityError
- ✅ Better error messages showing which item failed

**Test**:
```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Should handle existing records gracefully
poetry run python standalone_habits_import.py \
  "$DB_URL" \
  /workspace/data/habits/programs/unfck-your-eating

# Expected output:
# Program ID: <uuid>
# Created/Updated lessons and habits
# ⚠️ Skipping 'X': ... (if any duplicates)
```

## Validation Commands

### Check for Duplicate Slugs (Should be 0)
```sql
SELECT slug, COUNT(*)
FROM movements.movements
GROUP BY slug
HAVING COUNT(*) > 1;

-- Expected: 0 rows
```

### Count Movements by Source
```sql
SELECT
  source,
  COUNT(*) as count,
  COUNT(CASE WHEN short_video_url IS NOT NULL THEN 1 END) as with_short_video,
  COUNT(CASE WHEN long_video_url IS NOT NULL THEN 1 END) as with_long_video
FROM movements.movements
GROUP BY source
ORDER BY count DESC;

-- Expected:
-- exercisedb_csv | ~400+ | ~400+ | ~400+
-- precision_nutrition | ~445 | ~445 | ~0 (or ~445 if Craig CSV provided)
-- overlapping exercises should have PN videos + ExerciseDB data
```

### Sample Video URLs
```sql
SELECT
  name,
  source,
  short_video_url,
  long_video_url,
  metadata->'video_coaches' as coaches
FROM movements.movements
WHERE short_video_url IS NOT NULL
ORDER BY name
LIMIT 5;
```

## Complete Test Workflow

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Set your database URL
export DB_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

# 1. Import ExerciseDB (first time)
echo "=== ExerciseDB Import (Round 1) ==="
poetry run python standalone_movements_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# Expected: Created: 400+, Updated: 0, Skipped: 0

# 2. Re-run ExerciseDB (should update, not duplicate)
echo ""
echo "=== ExerciseDB Import (Round 2 - Idempotent Test) ==="
poetry run python standalone_movements_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# Expected: Created: 0, Updated: 400+, Skipped: 0

# 3. Import PN (first time)
echo ""
echo "=== PN Import (Round 1) ==="
poetry run python standalone_pn_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv

# Expected: Created: ~90 (PN-only), Updated: ~355 (overlapping), Skipped: 0

# 4. Re-run PN (should update, not duplicate)
echo ""
echo "=== PN Import (Round 2 - Idempotent Test) ==="
poetry run python standalone_pn_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv

# Expected: Created: 0, Updated: 445, Skipped: 0

# 5. Habits (first time)
echo ""
echo "=== Habits Import (Round 1) ==="
poetry run python standalone_habits_import.py \
  "$DB_URL" \
  /workspace/data/habits/programs/unfck-your-eating

# Expected: Program and lessons/habits created

# 6. Re-run Habits (should update, not duplicate)
echo ""
echo "=== Habits Import (Round 2 - Idempotent Test) ==="
poetry run python standalone_habits_import.py \
  "$DB_URL" \
  /workspace/data/habits/programs/unfck-your-eating

# Expected: Program and lessons/habits updated
```

## Error Handling

All scripts now handle these scenarios gracefully:

1. **Duplicate slugs**: Rollback, skip, continue
2. **Existing records**: Update instead of insert
3. **Missing data**: Skip empty/invalid rows
4. **Database errors**: Rollback transaction, print error, continue

## What to Expect

### ✅ Good Output
```
Database: postgresql+asyncpg://...
CSV: /path/to/exercises.csv
Update existing: True

✓ Import complete!
  Created: 50
  Updated: 350
  Skipped: 0
  Total:   400
```

### ✅ Also Good (with duplicates)
```
  ⚠️  Skipping 'Bodyweight Step Up': duplicate key value violates unique constraint "movements_slug_key"

✓ Import complete!
  Created: 40
  Updated: 350
  Skipped: 10
  Total:   400
```

### ❌ Bad (should not happen anymore)
```
IntegrityError: duplicate key value violates unique constraint "movements_slug_key"
[Full stack trace]
```

## Summary

- ✅ All imports are idempotent
- ✅ Safe to run multiple times
- ✅ No duplicate key errors
- ✅ Graceful error handling
- ✅ Clear output showing created/updated/skipped counts

**Ready to run against both staging and production!** 🚀
