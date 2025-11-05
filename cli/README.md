# MindMirror CLI & Data Importers

A collection of tools for managing MindMirror knowledge bases and importing data (habits, movements, programs).

## 🚨 Important: Standalone Scripts (Preferred)

**We are moving away from the old CLI tooling in favor of standalone Python scripts.** These scripts are simpler, have no CLI dependencies, and are fully idempotent.

### ✅ Use Standalone Scripts For:
- **Movements Import** (ExerciseDB CSV, Precision Nutrition)
- **Habits/Programs Import**
- **Production & Staging Deployments**

### ⚠️ Old CLI Commands (Legacy)
The `mindmirror seed-*` commands are still available but will be phased out. Use standalone scripts instead.

---

## 🚀 Quick Start: Standalone Scripts (Recommended)

### Prerequisites

1. **Get Database URL** from Supabase dashboard (see critical requirements below)
2. **Set environment variable**:
   ```bash
   export DB_URL="postgresql+asyncpg://postgres.PROJECT_ID:[PASSWORD]@aws-REGION.pooler.supabase.com:5432/postgres"
   ```

---

## 🚨 CRITICAL: Database URL Requirements

**You MUST use Supabase Session Pooler URLs**, not direct connection URLs.

### ✅ Correct Format (Session Pooler):
```bash
export DB_URL="postgresql+asyncpg://postgres.PROJECT_ID:PASSWORD@aws-REGION.pooler.supabase.com:5432/postgres"

# Real example:
export DB_URL="postgresql+asyncpg://postgres.rdsamhbqstqgvezsbado:YOUR_PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
```

### ❌ Wrong Format (Direct Connection - DON'T USE):
```bash
# DON'T USE THIS - will fail with network errors
postgresql+asyncpg://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
```

### Why This Matters:
- ✅ **`+asyncpg` driver** required for async SQLAlchemy operations
- ✅ **Session pooler** (`pooler.supabase.com`) required for pgbouncer compatibility
- ✅ **Prevents errors**: "prepared statement already exists" (pgbouncer collision)
- ✅ **Prevents errors**: "Network is unreachable" / DNS failures (routing issues)

### Where to Find Your URL:
**Supabase Dashboard** → Project Settings → Database → Connection String → **Session Pooler** (NOT Transaction or Direct)

**Key Components**:
- Username format: `postgres.PROJECT_ID` (e.g., `postgres.rdsamhbqstqgvezsbado`)
- Host: `aws-REGION.pooler.supabase.com` (e.g., `aws-1-us-east-1.pooler.supabase.com`)
- Port: `5432` (Transaction pooler) or `6543` (Session pooler - **recommended**)
- Driver: `postgresql+asyncpg://` (**required** - not just `postgresql://`)

---

### Import Order (Important!)

For best results, import in this order:

1. ✅ **ExerciseDB first** (broad catalog with biomechanical data)
2. ✅ **Precision Nutrition second** (upgrades overlapping exercises with better videos)
3. ✅ **Habits/Programs** (any time)

**Why?** PN importer updates existing exercises. ExerciseDB → PN gives you ExerciseDB's biomechanical data + PN's high-quality Vimeo videos for overlapping exercises.

### 1. Import Movements from ExerciseDB CSV

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Staging
poetry run python standalone_movements_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# Production
poetry run python standalone_movements_import.py \
  "$PRODUCTION_DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv
```

**What it does**:
- Imports ~400+ exercises from ExerciseDB CSV
- Includes biomechanical attributes (muscle groups, movement patterns, difficulty)
- Adds YouTube video URLs (short demonstration + in-depth explanation)
- **Idempotent**: Safe to run multiple times

### 2. Import Precision Nutrition Movements (Jen Only - Recommended)

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Staging (Jen only)
poetry run python standalone_pn_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv

# Production (Jen only)
poetry run python standalone_pn_import.py \
  "$PRODUCTION_DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv
```

**What it does**:
- Imports ~445 exercises with Vimeo coach videos
- Jen's video becomes PRIMARY `short_video_url` (shown in UI)
- Updates existing exercises from ExerciseDB with PN videos
- Stores coach metadata in JSONB `metadata` column
- **Idempotent**: Safe to run multiple times

**Optional: Include Craig's videos as alternate**:
```bash
poetry run python standalone_pn_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/craig_export.csv
```
Craig's video becomes `long_video_url` (ALTERNATE/detailed version).

### 3. Import Habits/Programs

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Staging
poetry run python standalone_habits_import.py \
  "$DB_URL" \
  /workspace/data/habits/programs/unfck-your-eating

# Production
poetry run python standalone_habits_import.py \
  "$PRODUCTION_DB_URL" \
  /workspace/data/habits/programs/unfck-your-eating
```

**What it does**:
- Imports program, lessons, and habits from YAML
- Uses content hashing for idempotency
- **Idempotent**: Safe to run multiple times

---

## 📋 Video URL Strategy

### Database Schema
```python
short_video_url: str   # PRIMARY video shown in UI
long_video_url: str    # ALTERNATE/detailed video
metadata: dict         # JSONB for flexible data (coach info, source details)
```

### Video URL Mapping

**Precision Nutrition** (PN):
- Jen (female coach) → `short_video_url` ✅ **PRIMARY** (shown in UI)
- Craig (male coach) → `long_video_url` (ALTERNATE/detailed)
- Both stored in `metadata.video_coaches` as well

**ExerciseDB CSV**:
- "Short YouTube Demonstration" → `short_video_url`
- "In-Depth YouTube Explanation" → `long_video_url`

### Final State After Both Imports

| Exercise Type | Videos | Biomechanical Data |
|---------------|--------|-------------------|
| ExerciseDB-only (~50) | YouTube demos | ✅ Full attributes |
| PN-only (~90) | Jen's Vimeo (primary) | ❌ Limited |
| Overlapping (~355) | Jen's Vimeo (primary) | ✅ Full attributes |

**Best of both worlds**: PN's high-quality videos + ExerciseDB's biomechanical data!

---

## ✅ Idempotency & Error Handling

All standalone scripts are **truly idempotent**:

### How It Works
1. ✅ Queries by `slug` (unique constraint) instead of `name`
2. ✅ Wraps in `try/except IntegrityError` to catch duplicates
3. ✅ Uses `session.flush()` after each operation
4. ✅ Rollbacks on error and continues to next record
5. ✅ Prints warnings for skipped records

### Expected Output (Good)
```
✓ Import complete!
  Created: 50
  Updated: 350
  Skipped: 0
  Total:   400
```

Or with some duplicates (also fine):
```
  ⚠️  Skipping 'Bodyweight Step Up': duplicate key...

✓ Import complete!
  Created: 40
  Updated: 350
  Skipped: 10
  Total:   400
```

### No More Crashes!
**Before fix**:
```
IntegrityError: duplicate key value violates unique constraint "movements_slug_key"
[Stack trace crash]
```

**After fix**:
```
  ⚠️  Skipping 'Bodyweight Step Up': duplicate key...
[Continues gracefully]
```

---

## 🧪 Validation & Testing

### Pre-Flight Check: Verify `metadata` Column Exists

```sql
-- Check if metadata column exists
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

-- Expected result:
-- movements | movements | metadata | jsonb | YES

-- If no rows returned, run migration:
```

### Run Migration (If Needed)

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/movements_service

# Check current migration version
poetry run alembic current

# Run migration
poetry run alembic upgrade head

# Verify (should show: 0002_add_metadata_jsonb)
poetry run alembic current
```

### Post-Import Validation

```sql
-- Check for duplicate slugs (should be 0)
SELECT slug, COUNT(*)
FROM movements.movements
GROUP BY slug
HAVING COUNT(*) > 1;

-- Count by source
SELECT
  source,
  COUNT(*) as count,
  COUNT(CASE WHEN short_video_url IS NOT NULL THEN 1 END) as with_video
FROM movements.movements
GROUP BY source
ORDER BY count DESC;

-- Sample video URLs
SELECT
  name,
  source,
  short_video_url,
  long_video_url,
  metadata->'video_coaches' as coaches
FROM movements.movements
WHERE short_video_url IS NOT NULL
LIMIT 10;
```

---

## 📝 Complete Import Workflow

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/cli

# Set database URL (Session Pooler - REQUIRED)
export DB_URL="postgresql+asyncpg://postgres.PROJECT_ID:[PASSWORD]@aws-REGION.pooler.supabase.com:5432/postgres"

# 1. ExerciseDB (broad catalog with biomechanical data)
poetry run python standalone_movements_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/exercises.csv

# Expected: Created: 400+, Updated: 0, Skipped: 0

# 2. Precision Nutrition (better videos - Jen only)
poetry run python standalone_pn_import.py \
  "$DB_URL" \
  /home/peleke/Documents/Projects/swae/MindMirror/data/fitness/pn/data/jen_export.csv

# Expected: Created: ~90, Updated: ~355, Skipped: 0

# 3. Habits/Programs
poetry run python standalone_habits_import.py \
  "$DB_URL" \
  /workspace/data/habits/programs/unfck-your-eating

# Expected: ✓ Import complete!
```

---

## 🔍 Troubleshooting

### Import Fails with "No module named 'movements'"
- Run from `cli/` directory
- Scripts add paths automatically

### Database Connection Fails
- ✅ **MUST use Session Pooler URL** (see "CRITICAL: Database URL Requirements" section above)
- ✅ Correct format: `postgresql+asyncpg://postgres.PROJECT_ID:PASSWORD@aws-REGION.pooler.supabase.com:5432/postgres`
- ❌ Direct connection URLs will fail with network errors
- Check Supabase IP allowlist (if using direct connection - not recommended)

### CSV Not Found
- Use absolute paths
- Verify: `ls -la /path/to/file.csv`

### "column metadata does not exist"
- Run Alembic migration (see "Pre-Flight Check" section)

### Duplicate Key Errors
- Should not happen anymore! Scripts handle gracefully.
- If you see crashes, check that you're using latest version of scripts.

---

## 📚 Additional Documentation

Detailed technical documentation:

- **STANDALONE_IMPORTERS.md** - Standalone scripts usage and troubleshooting
- **VIDEO_URL_HANDLING.md** - Video URL strategy and mapping details
- **IMPORT_STRATEGY.md** - Technical breakdown of import logic
- **IDEMPOTENT_FIXES.md** - Changelog for idempotent fixes

---

## ⚙️ Legacy CLI Commands (Deprecated)

> **⚠️ Warning**: These commands are deprecated. Use standalone scripts instead.

The old CLI tooling (`mindmirror seed-*` commands) is still available but will be phased out in favor of standalone scripts, which are:
- ✅ Simpler (no CLI framework dependencies)
- ✅ More reliable (direct database access)
- ✅ Fully idempotent (safe to re-run)
- ✅ Better error handling

### Legacy: Qdrant Knowledge Base Management (Still Active)

These commands are still the recommended way to manage Qdrant knowledge bases:

```bash
# Check if everything is working
poetry run mindmirror qdrant health

# List available traditions
poetry run mindmirror qdrant list-traditions

# Build knowledge base for a specific tradition
poetry run mindmirror qdrant build --tradition canon-default --verbose

# Build all traditions
poetry run mindmirror qdrant build --verbose
```

### Legacy: Seeding Commands (Use Standalone Scripts Instead)

<details>
<summary>Click to expand legacy CLI seeding commands (deprecated)</summary>

#### `mindmirror seed-habits` (DEPRECATED)

Use `standalone_habits_import.py` instead.

```bash
# Old way (deprecated)
poetry run mindmirror seed-habits run /data/programs/my-program --env staging

# New way (recommended)
poetry run python standalone_habits_import.py "$DB_URL" /data/programs/my-program
```

#### `mindmirror seed-movements` (DEPRECATED)

Use `standalone_movements_import.py` instead.

```bash
# Old way (deprecated)
poetry run mindmirror seed-movements --from-csv data.csv --env staging

# New way (recommended)
poetry run python standalone_movements_import.py "$DB_URL" data.csv
```

#### `mindmirror seed-pn-movements` (DEPRECATED)

Use `standalone_pn_import.py` instead.

```bash
# Old way (deprecated)
poetry run mindmirror seed-pn-movements --jen-csv jen.csv --craig-csv craig.csv --env staging

# New way (recommended)
poetry run python standalone_pn_import.py "$DB_URL" jen.csv craig.csv
```

</details>

---

## 🛠️ Development

### Installation

```bash
cd cli
poetry install
```

### Running Tests

```bash
cd cli
poetry run pytest
```

### Code Formatting

```bash
cd cli
poetry run black src/
poetry run isort src/
```

### Type Checking

```bash
cd cli
poetry run mypy src/
```

---

## 📦 Environment Configuration

### Database URLs

Create `.env` file in `cli/` directory:

```bash
# Staging (Session Pooler - REQUIRED)
STAGING_DATABASE_URL="postgresql+asyncpg://postgres.PROJECT_ID:[PASSWORD]@aws-REGION.pooler.supabase.com:5432/postgres"

# Production (Session Pooler - REQUIRED)
PRODUCTION_DATABASE_URL="postgresql+asyncpg://postgres.PROJECT_ID:[PASSWORD]@aws-REGION.pooler.supabase.com:5432/postgres"

# Example (real format):
# STAGING_DATABASE_URL="postgresql+asyncpg://postgres.rdsamhbqstqgvezsbado:YOUR_PASSWORD@aws-1-us-east-1.pooler.supabase.com:5432/postgres"
```

**⚠️ CRITICAL**: Use Session Pooler URLs only! See "CRITICAL: Database URL Requirements" section above.

### Qdrant Configuration

```bash
# Local Qdrant (Docker)
QDRANT_URL="http://localhost:6333"

# Live Qdrant (Cloud)
LIVE_QDRANT_URL="https://[YOUR_CLUSTER].qdrant.io:6333"
QDRANT_API_KEY="[YOUR_API_KEY]"
```

### Embedding Configuration

```bash
# OpenAI (recommended)
EMBEDDING_PROVIDER="openai"
OPENAI_API_KEY="your-openai-api-key"

# Ollama (local)
EMBEDDING_PROVIDER="ollama"
OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
OLLAMA_BASE_URL="http://localhost:11434"
```

---

## 📂 Project Structure

```
cli/
├── README.md                           # This file
├── STANDALONE_IMPORTERS.md             # Standalone scripts docs
├── VIDEO_URL_HANDLING.md               # Video URL strategy
├── IMPORT_STRATEGY.md                  # Import logic breakdown
├── IDEMPOTENT_FIXES.md                 # Idempotency changelog
├── standalone_movements_import.py      # ExerciseDB CSV importer ✅
├── standalone_pn_import.py             # PN movements importer ✅
├── standalone_habits_import.py         # Habits/programs importer ✅
├── pyproject.toml                      # Poetry dependencies
├── src/
│   └── mindmirror_cli/                 # Legacy CLI commands
│       ├── commands/
│       │   ├── seed_habits.py          # Deprecated
│       │   ├── seed_movements.py       # Deprecated
│       │   └── seed_pn_movements.py    # Deprecated
│       └── qdrant/                     # Still active
│           ├── build.py
│           └── health.py
└── tests/
```

---

## 🎯 Summary

### ✅ Use Standalone Scripts (Recommended)
- `standalone_movements_import.py` - ExerciseDB CSV
- `standalone_pn_import.py` - Precision Nutrition
- `standalone_habits_import.py` - Habits/Programs

### ✅ Use CLI Commands (Active)
- `mindmirror qdrant build` - Knowledge base management
- `mindmirror qdrant health` - Qdrant monitoring
- `mindmirror qdrant list-traditions` - Tradition discovery

### ⚠️ Avoid (Deprecated)
- `mindmirror seed-habits` - Use `standalone_habits_import.py`
- `mindmirror seed-movements` - Use `standalone_movements_import.py`
- `mindmirror seed-pn-movements` - Use `standalone_pn_import.py`

---

## 🚀 Ready to Import!

1. ✅ Set `$DB_URL` environment variable (**Session Pooler URL - see critical requirements above**)
2. ✅ Run migration if needed (`alembic upgrade head`)
3. ✅ Import ExerciseDB first
4. ✅ Import PN second (Jen only recommended)
5. ✅ Import habits/programs
6. ✅ Validate with SQL queries

**All scripts are idempotent - safe to run multiple times!** 🎉

---

## License

This project is part of MindMirror and follows the same license terms.
