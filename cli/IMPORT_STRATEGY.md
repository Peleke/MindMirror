# Movement Import Strategy - Video URL Handling

## Schema Fields
```python
short_video_url: str   # PRIMARY video shown in UI
long_video_url: str    # ALTERNATE/detailed video
metadata_: dict        # JSONB for flexible data
```

## Data Sources

### 1. PN Movements (Precision Nutrition)
**Files**: `jen_export.csv`, `craig_export.csv`

**Current Implementation** (movements_service/movements/service/pn_csv_importer.py:125-126):
```python
'short_video_url': craig_url or None,  # male coach
'long_video_url': jen_url or None,     # female coach
```

**❌ PROBLEM**: You want Jen as PRIMARY, not Craig!

**✅ SHOULD BE**:
```python
'short_video_url': jen_url or None,    # female coach (PRIMARY)
'long_video_url': craig_url or None,   # male coach (ALTERNATE)
```

**Metadata Storage**:
```json
{
  "video_coaches": {
    "female": "https://vimeo.com/111032083",
    "male": "https://vimeo.com/121807106"
  },
  "source_details": {
    "program": "precision_nutrition",
    "import_version": "v1"
  }
}
```

### 2. ExerciseDB CSV
**File**: `data/fitness/exercises.csv`

**CSV Columns** (line 16):
- "Short YouTube Demonstration" → `short_video_url`
- "In-Depth YouTube Explanation" → `long_video_url`

**Current Implementation** (movements_service/movements/service/csv_importer.py):
- ❌ **DOESN'T IMPORT VIDEOS AT ALL!**

**✅ SHOULD BE**:
```python
'short_video_url': row.get('Short YouTube Demonstration'),
'long_video_url': row.get('In-Depth YouTube Explanation'),
'source': 'exercisedb_csv',
```

## Import Order & Strategy

### Recommended Approach:

1. **Import ExerciseDB FIRST** (broader catalog, biomechanical data)
2. **Import PN SECOND** (updates with better videos where overlaps exist)

### Why This Order?

- ExerciseDB has ~400+ exercises with biomechanical attributes
- PN has ~445 exercises with high-quality coach videos
- Many exercises overlap (same names)
- PN importer has `update_existing=True` by default
- Result: ExerciseDB exercises get upgraded with PN videos

### Example Flow:

```bash
# Step 1: Import ExerciseDB (broad catalog)
poetry run python standalone_movements_import.py "$DB_URL" exercises.csv
# Created: 400, Updated: 0, Skipped: 0

# Step 2: Import PN (better videos)
poetry run python standalone_pn_import.py "$DB_URL" jen_export.csv
# Created: 45 (PN-only exercises)
# Updated: 355 (overlapping exercises now have PN videos)
# Skipped: 0
```

**Final State**:
- ExerciseDB-only exercises: ExerciseDB YouTube videos
- PN-only exercises: PN Vimeo videos (Jen primary)
- Overlapping exercises: PN Vimeo videos (Jen primary) + ExerciseDB biomechanical data

## What Needs Fixing

### Fix #1: ExerciseDB Importer (standalone_movements_import.py)
**Current**: No video import
**Fix**: Add video URL mapping

### Fix #2: PN Importer (pn_csv_importer.py lines 125-126)
**Current**: Craig = short, Jen = long
**Fix**: Jen = short, Craig = long

### Fix #3: Standalone PN Script
**Current**: Requires both CSVs
**Fix**: Make Craig optional, Jen-only works

## Implementation Status

- [ ] Fix standalone_movements_import.py (add video URLs)
- [ ] Fix pn_csv_importer.py (flip Jen/Craig)
- [ ] Update standalone_pn_import.py (optional Craig)
- [ ] Test both imports
- [ ] Document final usage
