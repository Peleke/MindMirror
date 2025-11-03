# Video URL Handling - Complete Guide

## TL;DR

**Fixed! Here's how it works:**

1. **PN Movements**: Jen's video → `shortVideoUrl` (PRIMARY displayed in UI)
2. **ExerciseDB**: "Short YouTube Demo" → `shortVideoUrl`, "In-Depth" → `longVideoUrl`
3. **Both** import into `movements.movements` table
4. **Import order**: ExerciseDB first, then PN (upgrades overlapping exercises with better videos)

## Database Schema

```sql
-- movements.movements table
CREATE TABLE movements.movements (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    slug VARCHAR UNIQUE NOT NULL,

    -- Video URLs
    short_video_url VARCHAR,  -- PRIMARY video (shown in UI)
    long_video_url VARCHAR,   -- ALTERNATE/detailed video

    -- Flexible metadata
    metadata JSONB,

    -- Other fields...
    source VARCHAR,
    description TEXT,
    difficulty VARCHAR,
    -- ... biomechanical attributes ...
);
```

## Import Strategy

### Step 1: Import ExerciseDB (Broad Catalog)

**File**: `/home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv`

**Video Mapping**:
```
CSV Column                        → Database Field
"Short YouTube Demonstration"     → short_video_url
"In-Depth YouTube Explanation"    → long_video_url
```

**Example Row**:
```csv
Exercise: "Bodyweight Glute Bridge"
Short YouTube Demonstration: "https://youtube.com/watch?v=abc123"
In-Depth YouTube Explanation: "https://youtube.com/watch?v=xyz789"
```

**Result in DB**:
```python
{
    "name": "Bodyweight Glute Bridge",
    "short_video_url": "https://youtube.com/watch?v=abc123",
    "long_video_url": "https://youtube.com/watch?v=xyz789",
    "source": "exercisedb_csv",
    "difficulty": "Beginner",
    "body_region": "Lower Body",
    # ... biomechanical data ...
}
```

**Command**:
```bash
poetry run python standalone_movements_import.py \
  "$DATABASE_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv
```

### Step 2: Import PN (Better Videos, Jen Only)

**Files**:
- `/home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv`
- `/home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/craig_export.csv` (optional)

**Video Mapping**:
```
Jen's CSV URL   → short_video_url (PRIMARY)
Craig's CSV URL → long_video_url (ALTERNATE - optional)
```

**Example CSVs**:
```csv
# jen_export.csv
Exercise,URL,Description
Ab Wheel Iso,https://vimeo.com/111032083,"1. Lock ribs. 2. Tuck tailbone."

# craig_export.csv
Exercise,URL,Description
Ab Wheel Iso,https://vimeo.com/121807106,"1. Lock ribs. 2. Tuck tailbone."
```

**Result in DB** (Jen only):
```python
{
    "name": "Ab Wheel Iso",
    "short_video_url": "https://vimeo.com/111032083",  # Jen (PRIMARY)
    "long_video_url": None,                             # No Craig
    "source": "precision_nutrition",
    "description": "1. Lock ribs.\n2. Tuck tailbone.",
    "metadata": {
        "video_coaches": {
            "female": "https://vimeo.com/111032083"
        },
        "source_details": {
            "program": "precision_nutrition",
            "import_version": "v1"
        }
    }
}
```

**Result in DB** (Both coaches):
```python
{
    "name": "Ab Wheel Iso",
    "short_video_url": "https://vimeo.com/111032083",  # Jen (PRIMARY)
    "long_video_url": "https://vimeo.com/121807106",   # Craig (ALTERNATE)
    "source": "precision_nutrition",
    "metadata": {
        "video_coaches": {
            "female": "https://vimeo.com/111032083",
            "male": "https://vimeo.com/121807106"
        }
    }
}
```

**Command (Jen only - RECOMMENDED)**:
```bash
poetry run python standalone_pn_import.py \
  "$DATABASE_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv
```

**Command (Both coaches)**:
```bash
poetry run python standalone_pn_import.py \
  "$DATABASE_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/craig_export.csv
```

## What Happens with Overlapping Exercises?

**Scenario**: Exercise exists in both ExerciseDB and PN

**Example**: "Bodyweight Glute Bridge"

1. **After ExerciseDB import**:
```python
{
    "name": "Bodyweight Glute Bridge",
    "short_video_url": "https://youtube.com/...",
    "long_video_url": "https://youtube.com/...",
    "source": "exercisedb_csv",
    "difficulty": "Beginner",
    "body_region": "Lower Body",
    # ... all biomechanical data ...
}
```

2. **After PN import** (with `update_existing=True`):
```python
{
    "name": "Bodyweight Glute Bridge",
    "short_video_url": "https://vimeo.com/...",     # UPDATED to Jen's video
    "long_video_url": "https://vimeo.com/...",      # UPDATED to Craig's video (or None)
    "source": "precision_nutrition",                 # UPDATED
    "description": "1. Lock ribs.\n2. Tuck tailbone.", # UPDATED
    "difficulty": "Beginner",                        # PRESERVED from ExerciseDB
    "body_region": "Lower Body",                     # PRESERVED from ExerciseDB
    # ... all biomechanical data PRESERVED ...
}
```

**Result**: Best of both worlds! PN videos + ExerciseDB biomechanical data.

## Frontend Usage

**In your React/React Native app**:

```typescript
// Display primary video (what user sees first)
const primaryVideoUrl = movement.short_video_url;

// Optional: Show alternate/detailed video
const detailedVideoUrl = movement.long_video_url;

// Example component
function ExerciseCard({ movement }) {
  return (
    <div>
      <h2>{movement.name}</h2>

      {/* Primary video (always show this) */}
      <VideoPlayer url={movement.short_video_url} />

      {/* Optional detailed video */}
      {movement.long_video_url && (
        <Button onClick={() => showDetailedVideo(movement.long_video_url)}>
          Watch Detailed Version
        </Button>
      )}
    </div>
  );
}
```

## Implementation Status

✅ **FIXED**: PN importer now uses Jen as PRIMARY (movements_service/movements/service/pn_csv_importer.py:125-126)
✅ **FIXED**: ExerciseDB importer now imports video URLs (standalone_movements_import.py:91-92)
✅ **FIXED**: Standalone PN script supports Jen-only mode (standalone_pn_import.py)
✅ **VERIFIED**: Both importers write to same schema (`movements.movements`)

## Quick Reference

**Import to Staging**:
```bash
export STAGING_DB="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

# 1. ExerciseDB first
poetry run python standalone_movements_import.py "$STAGING_DB" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# 2. PN second (Jen only)
poetry run python standalone_pn_import.py "$STAGING_DB" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv
```

**Import to Production** (same commands, just change DB URL):
```bash
export PRODUCTION_DB="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

poetry run python standalone_movements_import.py "$PRODUCTION_DB" exercises.csv
poetry run python standalone_pn_import.py "$PRODUCTION_DB" jen_export.csv
```

## Verification SQL

```sql
-- Check video URL population
SELECT
  name,
  short_video_url,
  long_video_url,
  source,
  metadata->'video_coaches' as coaches
FROM movements.movements
WHERE short_video_url IS NOT NULL
LIMIT 10;

-- Count by source
SELECT
  source,
  COUNT(*) as count,
  COUNT(short_video_url) as has_short_video,
  COUNT(long_video_url) as has_long_video
FROM movements.movements
GROUP BY source;
```

Expected results:
```
source              | count | has_short_video | has_long_video
--------------------|-------|-----------------|---------------
exercisedb_csv      | 50    | 50              | 50
precision_nutrition | 445   | 445             | 0 (or 445 if Craig included)
```
