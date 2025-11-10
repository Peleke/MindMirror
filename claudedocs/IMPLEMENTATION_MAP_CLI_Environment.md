# Implementation Map: CLI Environment Improvements

**Epic**: EPIC_CLI_Environment_Improvements.md
**Date**: 2025-11-02
**Estimated Time**: 2-3 hours

---

## ✅ Pre-Implementation Verification

### seed-pn-movements Data Flow Analysis

**Question**: Does `seed-pn-movements` actually seed movements correctly?

**Answer**: ✅ **YES** - Verified data flow:

1. **CSV Parsing** (`pn_csv_importer.py:62-83`):
   - Reads Jen CSV: Exercise name → URL (female coach) + Description
   - Reads Craig CSV: Exercise name → URL (male coach) + Description
   - Merges by exercise name

2. **Movement Creation** (`pn_csv_importer.py:122-129`):
   ```python
   movement_data = {
       'name': exercise_name,
       'description': cleaned_description,
       'short_video_url': craig_url,      # male coach
       'long_video_url': jen_url,          # female coach
       'source': 'precision_nutrition',
       'metadata': {...}
   }
   ```

3. **Repository Create** (`movements_repo.py:260-298`):
   - Creates `MovementModel` with all fields
   - Sets `shortVideoUrl` and `longVideoUrl` correctly
   - Commits to `movements` schema in PostgreSQL

**Conclusion**: `seed-pn-movements` works correctly! It:
- ✅ Parses dual coach videos (Jen female, Craig male)
- ✅ Creates movements in movements_service database
- ✅ Stores video URLs in correct fields
- ✅ Handles updates vs creates via `update_existing` flag

---

## 📁 File Change Map

### Phase 1: Core Infrastructure (45 mins)

#### File 1: `cli/src/mindmirror_cli/core/utils.py`
**Lines to modify**: 11-44 (entire file rewrite)
**Changes**:
- Update `_current_environment` to support `local|staging|production`
- Add `get_database_url(service: str)` helper
- Add `is_production_environment()` safety check
- Update `set_environment()` validation
- Deprecate binary `is_live_environment()` (keep for backwards compat)

**New functions to add**:
```python
def get_database_url(service: str = 'main') -> str
def is_production_environment() -> bool
def is_staging_environment() -> bool
```

**Environment variable patterns**:
```
LOCAL_DATABASE_URL
LOCAL_MOVEMENTS_DATABASE_URL
STAGING_DATABASE_URL
STAGING_MOVEMENTS_DATABASE_URL
PRODUCTION_DATABASE_URL
PRODUCTION_MOVEMENTS_DATABASE_URL
```

---

### Phase 2: Command Updates (60 mins)

#### File 2: `cli/src/mindmirror_cli/commands/seed_habits.py`
**Lines to modify**:
- Line 59-82: `run()` function parameter and logic
- Line 64-82: Database URL resolution logic

**Changes**:
1. Update `env` parameter help text to show `local|staging|production`
2. Replace manual database URL logic with `get_database_url('main')`
3. Add production safety prompt before execution
4. Update console messages

**New code section** (lines 64-84):
```python
async def _run():
    if env:
        set_environment(env)
        console.print(f"[blue]Environment: {get_current_environment()}[/blue]")

    # Production safety check
    if is_production_environment():
        confirm = typer.confirm(
            "⚠️  You are seeding PRODUCTION habits/programs. Continue?",
            default=False
        )
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    nonlocal database_url
    if not database_url:
        try:
            database_url = get_database_url('main')
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

    console.print(f"[cyan]Target DB:[/cyan] {database_url.split('@')[-1]}")
    # ... rest of implementation
```

---

#### File 3: `cli/src/mindmirror_cli/commands/seed_movements.py`
**Lines to modify**:
- Line 72: Update `env` parameter help text
- Line 23-36: Database URL resolution in `_execute()`

**Changes**:
1. Update help text: `"Environment (local, staging, production)"`
2. Replace database URL logic with `get_database_url('movements')`
3. Add production safety prompt
4. Improve error messages

**New code section** (lines 23-42):
```python
async def _execute(from_csv: str, database_url: Optional[str], schema: str, env: Optional[str]):
    if env:
        set_environment(env)
        console.print(f"[blue]Environment: {get_current_environment()}[/blue]")

    # Production safety check
    if is_production_environment():
        confirm = typer.confirm(
            f"⚠️  You are seeding PRODUCTION movements from {from_csv}. Continue?",
            default=False
        )
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    if not database_url:
        try:
            database_url = get_database_url('movements')
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

    console.print(f"[cyan]Target DB:[/cyan] {database_url.split('@')[-1]}")
    # ... rest
```

---

#### File 4: `cli/src/mindmirror_cli/commands/seed_pn_movements.py`
**Lines to modify**:
- Line 119: Update `env` parameter help text
- Line 30-52: Database URL resolution in `_execute()`

**Changes**:
1. Update help text: `"Environment (local, staging, production)"`
2. Replace database URL logic with `get_database_url('movements')`
3. Add production safety prompt
4. Standardize error handling

**New code section** (lines 31-52):
```python
async def _execute(...):
    if env:
        set_environment(env)
        console.print(f"[blue]Environment: {get_current_environment()}[/blue]")

    # Production safety check
    if is_production_environment():
        confirm = typer.confirm(
            "⚠️  You are seeding PRODUCTION Precision Nutrition movements. Continue?",
            default=False
        )
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    if not database_url:
        try:
            database_url = get_database_url('movements')
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

    console.print(f"[cyan]Target DB:[/cyan] {database_url.split('@')[-1]}")
    # ... rest
```

---

### Phase 3: Documentation (30 mins)

#### File 5: `cli/README.md` (NEW or UPDATE)
**Create if doesn't exist, or add new section**

**Content to add**:
```markdown
## Environment Configuration

### Supported Environments

- **local**: Docker Compose (automatic defaults, no config needed)
- **staging**: Staging environment (requires env vars)
- **production**: Production environment (requires env vars + confirmation prompt)

### Environment Variables

Create a `.env` file in the `cli/` directory:

# === Staging Environment ===
STAGING_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"
STAGING_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

# === Production Environment ===
PRODUCTION_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"
PRODUCTION_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

### Seeding Examples

# Local (Docker) - no configuration needed
poetry run mindmirror seed-habits run /data/programs/my-program --env local
poetry run mindmirror seed-movements --from-csv data.csv --env local
poetry run mindmirror seed-pn-movements --jen-csv jen.csv --craig-csv craig.csv --env local

# Staging
poetry run mindmirror seed-habits run /data/programs/my-program --env staging
poetry run mindmirror seed-movements --from-csv data.csv --env staging

# Production (requires confirmation)
poetry run mindmirror seed-habits run /data/programs/my-program --env production
⚠️  You are seeding PRODUCTION. Continue? [y/N]:
```

---

#### File 6: `cli/.env.example` (NEW)
**Create new file**

**Full content**:
```bash
# MindMirror CLI Environment Configuration
# Copy this file to .env and fill in your values

# === Local Environment (Docker Compose) ===
# No configuration needed - automatic defaults used
# LOCAL_DATABASE_URL is optional override

# === Staging Environment ===
# Main database (habits, journal, agent services)
STAGING_DATABASE_URL="postgresql+asyncpg://postgres:[YOUR_PASSWORD]@[STAGING_HOST]:5432/postgres"

# Movements service database
STAGING_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[YOUR_PASSWORD]@[STAGING_HOST]:5432/postgres"

# === Production Environment ===
# Main database (habits, journal, agent services)
PRODUCTION_DATABASE_URL="postgresql+asyncpg://postgres:[YOUR_PASSWORD]@[PRODUCTION_HOST]:5432/postgres"

# Movements service database
PRODUCTION_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[YOUR_PASSWORD]@[PRODUCTION_HOST]:5432/postgres"

# === Legacy Support (backwards compatibility) ===
# SUPABASE_DATABASE_URL is used as fallback if environment-specific URLs not set
# SUPABASE_DATABASE_URL="postgresql+asyncpg://..."

# === Qdrant Configuration ===
# Local Qdrant (Docker)
QDRANT_URL="http://localhost:6333"

# Live Qdrant (Cloud)
LIVE_QDRANT_URL="https://[YOUR_CLUSTER].qdrant.io:6333"
QDRANT_API_KEY="[YOUR_API_KEY]"
```

---

## 🔄 Implementation Order

### Step-by-Step Execution Plan

1. **Phase 1: Core Infrastructure** (45 mins)
   - [ ] Update `cli/src/mindmirror_cli/core/utils.py`
   - [ ] Test environment switching with simple script
   - [ ] Verify `get_database_url()` fallback logic

2. **Phase 2: Command Updates** (60 mins)
   - [ ] Update `seed_habits.py`
   - [ ] Update `seed_movements.py`
   - [ ] Update `seed_pn_movements.py`
   - [ ] Test each command with `--env local` (should work without changes)

3. **Phase 3: Documentation** (30 mins)
   - [ ] Create/update `cli/README.md`
   - [ ] Create `cli/.env.example`
   - [ ] Test complete workflow: local → staging (with env vars)

---

## ✅ Testing Checklist

After each phase:

### Phase 1 Tests
```bash
cd cli
poetry run python -c "from mindmirror_cli.core.utils import *; set_environment('local'); print(get_database_url('main'))"
poetry run python -c "from mindmirror_cli.core.utils import *; set_environment('staging'); print(get_database_url('movements'))"
```

### Phase 2 Tests (Local Environment)
```bash
# Should work without env vars (Docker defaults)
poetry run mindmirror seed-habits run /workspace/data/habits/programs/test --env local --help
poetry run mindmirror seed-movements --help
poetry run mindmirror seed-pn-movements --help
```

### Phase 3 Tests (Full Workflow)
```bash
# Test staging with env vars
export STAGING_DATABASE_URL="postgresql+asyncpg://test@localhost:5432/test"
poetry run mindmirror seed-habits run /data/test --env staging
# Should show error (DB unreachable) but correct URL parsing

# Test production safety prompt
export PRODUCTION_DATABASE_URL="postgresql+asyncpg://test@localhost:5432/test"
poetry run mindmirror seed-habits run /data/test --env production
# Should prompt: "⚠️  You are seeding PRODUCTION. Continue? [y/N]:"
# Press 'n' to verify cancellation works
```

---

## 🚨 Risks & Mitigations

### Risk 1: Breaking Existing Workflows
**Mitigation**: Keep backwards compatibility
- `is_live_environment()` still works (checks for staging OR production)
- `SUPABASE_DATABASE_URL` fallback maintained
- `--db-url` explicit override still works

### Risk 2: Accidental Production Seeds
**Mitigation**: Multiple safety layers
- Production env requires explicit `--env production`
- Confirmation prompt before execution
- Clear console messages showing target environment

### Risk 3: Missing Environment Variables
**Mitigation**: Helpful error messages
- Show which env var to set
- Include example in error message
- Provide `.env.example` template

---

## 📊 Success Criteria

- [ ] All three environments work correctly (local/staging/production)
- [ ] No environment variables needed for local Docker
- [ ] Production prompts for confirmation
- [ ] Clear error messages for missing config
- [ ] Backwards compatible with existing setups
- [ ] Documentation covers all use cases

---

## 🎯 Ready to Implement

All files mapped, changes documented, test plan ready.

**Total files to modify**: 4
**Total files to create**: 2
**Estimated time**: 2-3 hours
**Risk level**: Low (backwards compatible)

Ready to start Phase 1! 🚀
