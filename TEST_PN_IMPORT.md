# Testing PN Movements Import

## What Was Built

### 1. Schema Changes ✅
- **File**: `movements_service/movements/repository/models.py`
- **Change**: Added `metadata_: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, name="metadata")`
- **Purpose**: Store coach video mappings and flexible metadata

### 2. Migration ✅
- **File**: `movements_service/alembic/versions/0002_add_metadata_jsonb.py`
- **SQL**: `ALTER TABLE movements.movements ADD COLUMN metadata JSONB`
- **Reversible**: Yes, with `downgrade()`

### 3. PN CSV Importer ✅
- **File**: `movements_service/movements/service/pn_csv_importer.py`
- **Features**:
  - Merges jen_export.csv (female coach) + craig_export.csv (male coach)
  - Parses numbered instructions: "1. Text. 2. Text." → "1. Text.\n2. Text."
  - Populates both `short_video_url`/`long_video_url` AND metadata
  - Handles create/update/skip logic
  - Sets `source = "precision_nutrition"`

### 4. CLI Command ✅
- **File**: `cli/src/mindmirror_cli/commands/seed_pn_movements.py`
- **Command**: `mindmirror seed-pn-movements`
- **Registered**: Added to main CLI app

## How to Test

### Step 1: Run the Migration

From movements_service directory:
```bash
cd movements_service
poetry run alembic upgrade head
```

Or via Docker (when services are running):
```bash
docker exec -it movements_service poetry run alembic upgrade head
```

### Step 2: Run the Import

From CLI directory:
```bash
cd cli
poetry run mindmirror seed-pn-movements \
  --jen-csv /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv \
  --craig-csv /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/craig_export.csv
```

Expected output:
```
Using environment: local
DB: movements_postgres:5432/swae_movements
Jen CSV: /home/peleke/.../jen_export.csv
Craig CSV: /home/peleke/.../craig_export.csv
Update existing: True
Importing PN movements...

✓ Import complete!
  Created: 445
  Updated: 0
  Skipped: 0
  Total:   445
```

### Step 3: Verify Data

Connect to DB and check:
```sql
-- Check metadata column exists
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'movements'
  AND table_name = 'movements'
  AND column_name = 'metadata';

-- Check sample movement
SELECT
  name,
  short_video_url,
  long_video_url,
  source,
  metadata->'video_coaches'->>'male' as male_coach_url,
  metadata->'video_coaches'->>'female' as female_coach_url,
  description
FROM movements.movements
WHERE name = 'Ab Wheel Iso'
LIMIT 1;
```

Expected result:
- `short_video_url`: Craig's Vimeo URL (121807106)
- `long_video_url`: Jen's Vimeo URL (111032083)
- `source`: "precision_nutrition"
- `metadata.video_coaches.male`: Same as short_video_url
- `metadata.video_coaches.female`: Same as long_video_url
- `description`: Multi-line formatted (newlines between steps)

### Step 4: Test Update Mode

Run import again with same CSVs:
```bash
poetry run mindmirror seed-pn-movements \
  --jen-csv .../jen_export.csv \
  --craig-csv .../craig_export.csv
```

Expected:
```
✓ Import complete!
  Created: 0
  Updated: 445
  Skipped: 0
  Total:   445
```

### Step 5: Test Skip Mode

Run with `--skip-existing` flag:
```bash
poetry run mindmirror seed-pn-movements \
  --jen-csv .../jen_export.csv \
  --craig-csv .../craig_export.csv \
  --skip-existing
```

Expected:
```
✓ Import complete!
  Created: 0
  Updated: 0
  Skipped: 445
  Total:   445
```

## Architecture Notes

### Metadata Structure
```json
{
  "video_coaches": {
    "male": "https://vimeo.com/121807106",
    "female": "https://vimeo.com/111032083"
  },
  "source_details": {
    "program": "precision_nutrition",
    "import_version": "v1"
  }
}
```

### Coach Video Mapping
- **male coach (Craig)** → `short_video_url` + `metadata.video_coaches.male`
- **female coach (Jen)** → `long_video_url` + `metadata.video_coaches.female`

This dual storage provides:
1. **Backwards compatibility**: Existing code using short/long URLs still works
2. **Semantic clarity**: GraphQL can expose `videoByCoachGender(gender: String)` resolver
3. **Future extensibility**: Add more coaches without schema changes

### Future Enhancements

Easy additions via metadata:
- Coach names: `metadata.coaches = {male: "Craig Rasmussen", female: "Jen Comas"}`
- Video production dates
- Difficulty progressions
- Equipment variations
- Certification levels

## Troubleshooting

### Import fails with "No module named 'movements'"
- Ensure you're running from CLI with movements_service in PYTHONPATH
- Or run via Docker where all paths are configured

### Migration fails with "relation already exists"
- Check current migration: `alembic current`
- If at 0002, you're good - column exists
- If at 0001, run: `alembic upgrade head`

### CSVs not found
- Use absolute paths or relative from CLI directory
- Check paths with `ls -la data/fitness/pn/data/*.csv`

## What's Next?

1. **GraphQL Schema**: Add resolver for coach-specific video URLs
2. **Frontend**: Add coach gender selector for video playback
3. **Migration in Prod**: Run migration against staging/prod DBs
4. **Additional Coaches**: Easy to add more coach videos via metadata
