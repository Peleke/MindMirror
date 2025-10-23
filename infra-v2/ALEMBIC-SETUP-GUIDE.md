# Alembic Setup & Migration Guide

**Status:** ✅ READY FOR MANUAL TESTING
**Date:** 2025-10-21
**Last Updated:** After config review

---

## TL;DR: Quick Alembic Refresher

```bash
# The 4 commands you'll use 99% of the time:

# 1. Check current migration status
alembic current

# 2. Create a new migration (auto-detect model changes)
alembic revision --autogenerate -m "description of change"

# 3. Apply migrations (upgrade to latest)
alembic upgrade head

# 4. Rollback migrations (downgrade one step)
alembic downgrade -1
```

---

## Existing Alembic Configurations - REVIEW RESULTS

### ✅ **src/alembic-config/** (Agent + Journal Services)

**Target Schema:** `journal` (configured in utils.py line 83)
**Database URL:** From `DATABASE_URL` env var
**Driver:** Auto-detects (asyncpg for Supabase, psycopg2 for local)
**Migration Count:** 1 migration file (3e41ce1dbfee_m.py)

**Configuration Quality:** ⚠️ **Complex but functional**

**Helper Files:**
- `alembic_config/utils.py` - Database URL resolution, environment detection
- `alembic_config/config.py` - Metadata aggregation from central models

**Issues Found:**
- ⚠️ References `from models import metadata` (line 44 of config.py)
  - Need to verify this import works
  - Might be missing model imports

**Recommendation:**
✅ Test this migration manually first to ensure it works

---

### ✅ **habits_service/alembic/**

**Target Schema:** `habits`
**Database URL:** From `habits_service.app.config.get_settings().database_url`
**Driver:** AsyncPG (uses `create_async_engine`)
**Migration Count:** 2 migrations
  - `189b1231afd4_bootstrap_tables.py`
  - `3b7a1d2e4f56_soft_delete_program_templates.py`

**Configuration Quality:** ✅ **Clean and modern**

**Key Features:**
- Uses async Alembic (asyncio.run)
- Auto-creates schema before migrations (line 56)
- Imports all models properly (line 13)

**Issues Found:**
- None! This is a good reference implementation.

**Recommendation:**
✅ Use as template for new configs

---

### ✅ **meals_service/alembic/**

**Target Schema:** `meals`
**Database URL:** From `meals.web.config.Config.DATABASE_URL`
**Driver:** AsyncPG (uses `AsyncEngine`)
**Migration Count:** 2 migrations
  - `0001_init.py`
  - `0002_off_fields.py`

**Configuration Quality:** ⚠️ **Functional but has deprecated API**

**Issues Found:**
- ⚠️ Line 64-66: Uses deprecated `AsyncEngine` constructor
  ```python
  # WRONG (deprecated):
  connectable = AsyncEngine(pool.NullPool, url=DATABASE_URL)

  # RIGHT (modern):
  from sqlalchemy.ext.asyncio import create_async_engine
  connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)
  ```

**Recommendation:**
⚠️ Fix deprecated API before production (see fix below)

---

### ✅ **movements_service/alembic/**

**Target Schema:** `movements`
**Database URL:** From `movements.web.config.Config.DATABASE_URL`
**Driver:** psycopg2 (sync, uses `engine_from_config`)
**Migration Count:** 1 migration
  - `0001_init.py`

**Configuration Quality:** ✅ **Simple and reliable**

**Key Features:**
- Uses sync Alembic (simpler, more stable)
- Sets DATABASE_URL in config.set_main_option (line 13)

**Issues Found:**
- None

**Recommendation:**
✅ Good reference for simple sync setup

---

## Configuration Patterns Summary

**Three distinct patterns used:**

### Pattern 1: Complex with Utilities (src/alembic-config)
```python
# Pros: Centralized configuration, multi-environment support
# Cons: More complexity, harder to debug
# Use when: Multiple services share Alembic config
```

### Pattern 2: Async with Schema Creation (habits, meals)
```python
# Pros: Modern async support, auto-creates schema
# Cons: Requires asyncio, slightly more complex
# Use when: Service uses AsyncPG/async SQLAlchemy
```

### Pattern 3: Simple Sync (movements)
```python
# Pros: Simple, stable, easy to debug
# Cons: No async support
# Use when: Service uses sync SQLAlchemy
```

---

## Recommended Pattern for New Configs

Use **Pattern 2 (Async with Schema Creation)** for:
- practices_service (uses async SQLAlchemy)
- users_service (uses async SQLAlchemy)

Based on habits_service template (it's the cleanest).

---

## Fix Required: meals_service Deprecated API

**File:** `meals_service/alembic/env.py`

**Lines 63-67 (WRONG):**
```python
async def run_migrations_online() -> None:
    connectable = AsyncEngine(
        pool.NullPool,
        url=DATABASE_URL,
    )
```

**Fixed version:**
```python
async def run_migrations_online() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )
```

---

## Alembic Quick Reference (For Manual Testing)

### 1. Check Migration Status

```bash
cd habits_service  # Or any service with Alembic

# Show current migration revision
poetry run alembic current

# Output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# 3b7a1d2e4f56 (head)  # ← Current revision

# Show migration history
poetry run alembic history

# Output:
# 189b1231afd4 -> 3b7a1d2e4f56 (head), soft_delete_program_templates
# <base> -> 189b1231afd4, bootstrap_tables
```

### 2. Create New Migration

```bash
# Auto-generate migration from model changes
poetry run alembic revision --autogenerate -m "add email column to users"

# Output:
# INFO  [alembic.autogenerate.compare] Detected added column 'users.email'
# Generating /path/to/alembic/versions/abc123def456_add_email_column_to_users.py ... done

# Manual migration (no autogenerate)
poetry run alembic revision -m "manual migration"
```

### 3. Apply Migrations

```bash
# Upgrade to latest (head)
poetry run alembic upgrade head

# Upgrade by 1 step
poetry run alembic upgrade +1

# Upgrade to specific revision
poetry run alembic upgrade abc123def456

# Dry-run (show SQL without executing)
poetry run alembic upgrade head --sql
```

### 4. Rollback Migrations

```bash
# Downgrade by 1 step
poetry run alembic downgrade -1

# Downgrade to specific revision
poetry run alembic downgrade abc123def456

# Downgrade to base (DANGER: drops all tables!)
poetry run alembic downgrade base

# Dry-run rollback
poetry run alembic downgrade -1 --sql
```

### 5. Other Useful Commands

```bash
# Show current heads (should only be one)
poetry run alembic heads

# Show base revisions
poetry run alembic show base

# Show specific revision details
poetry run alembic show abc123def456

# Stamp database with revision (without running migrations)
poetry run alembic stamp head
```

---

## Idempotency: Safe to Run Multiple Times

**Alembic migrations are idempotent by design:**

### How It Works

1. **alembic_version table** tracks applied migrations:
   ```sql
   CREATE TABLE habits.alembic_version (
     version_num VARCHAR(32) NOT NULL PRIMARY KEY
   );

   -- Example data:
   -- version_num
   -- 3b7a1d2e4f56
   ```

2. **`alembic upgrade head`** checks this table:
   ```python
   # Pseudo-code:
   current_revision = SELECT version_num FROM alembic_version

   if current_revision == target_revision:
       print("Already at head, nothing to do")
       exit(0)  # Success, no-op
   else:
       run_pending_migrations()
   ```

3. **Running twice is safe:**
   ```bash
   # First run
   $ poetry run alembic upgrade head
   INFO  [alembic.runtime.migration] Running upgrade 189b -> 3b7a, soft_delete
   # ✅ Applied migration

   # Second run (immediately after)
   $ poetry run alembic upgrade head
   INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
   # ✅ No-op, already at head
   ```

### Manual Testing Plan (Idempotency Test)

```bash
# Test 1: Run migration twice on same service
cd habits_service
poetry run alembic upgrade head  # Should apply
poetry run alembic upgrade head  # Should no-op

# Test 2: Run orchestration script twice
cd infra-v2/bootstrap
./03-run-migrations.sh  # First run
# ✅ All migrations applied

./03-run-migrations.sh  # Second run
# ✅ All migrations no-op (already at head)

# Test 3: Run subset manually, then full orchestration
cd habits_service
poetry run alembic upgrade head  # Manual

cd movements_service
poetry run alembic upgrade head  # Manual

cd ../../infra-v2/bootstrap
./03-run-migrations.sh  # Orchestration
# ✅ habits & movements: no-op (already at head)
# ✅ Others: apply migrations
```

**Result:** Safe to run migrations multiple times, in any order.

---

## Manual Testing Workflow (Recommended)

### Phase 1: Test 2 Services Manually

```bash
# 1. Test habits_service (has 2 migrations, good test case)
cd habits_service
export DATABASE_URL="postgresql://user:pass@host:5432/swae"
poetry run alembic current  # Check status
poetry run alembic upgrade head  # Apply
poetry run alembic current  # Verify

# 2. Test movements_service (sync Alembic, different pattern)
cd ../movements_service
export DATABASE_URL="postgresql://user:pass@host:5432/swae"
poetry run alembic current
poetry run alembic upgrade head
poetry run alembic current

# 3. Verify in database
psql "$DATABASE_URL" -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname IN ('habits', 'movements') ORDER BY schemaname, tablename;"

# Expected output:
#  schemaname |      tablename
# ------------+--------------------
#  habits     | alembic_version
#  habits     | habit_tracking
#  habits     | habits
#  movements  | alembic_version
#  movements  | exercises
#  movements  | movements
```

### Phase 2: Test Idempotency

```bash
# Run same migrations again (should no-op)
cd habits_service
poetry run alembic upgrade head  # ✅ Should say "Already at head"

cd ../movements_service
poetry run alembic upgrade head  # ✅ Should say "Already at head"
```

### Phase 3: Test Orchestration Script

```bash
# Run full orchestration (includes manual + remaining services)
cd infra-v2/bootstrap
export DATABASE_URL="postgresql://user:pass@host:5432/swae"
./03-run-migrations.sh

# Expected:
# ✅ habits_service: no-op (already done manually)
# ✅ movements_service: no-op (already done manually)
# ✅ src/alembic-config: apply migrations
# ✅ meals_service: apply migrations
# ⚠️ practices_service: SKIP (no config yet)
# ⚠️ users_service: SKIP (no config yet)
```

### Phase 4: Create New Configs & Test

```bash
# After creating practices_service and users_service configs:

# Test manually first
cd practices_service
poetry run alembic upgrade head

cd ../users_service
poetry run alembic upgrade head

# Then re-run orchestration (should no-op for all)
cd ../infra-v2/bootstrap
./03-run-migrations.sh
# ✅ All services: no-op (everything at head)
```

---

## Common Issues & Solutions

### Issue 1: "Target database is not up to date"

**Error:**
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**Cause:** Database has migrations that aren't in your alembic/versions/

**Solution:**
```bash
# Show what's in database
poetry run alembic current

# Show what's in code
poetry run alembic history

# If database is ahead, stamp it with correct version
poetry run alembic stamp head
```

### Issue 2: "Can't locate revision identified by 'abc123'"

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'abc123def456'
```

**Cause:** alembic_version table has revision that doesn't exist in code

**Solution:**
```bash
# Option A: Stamp with existing revision
poetry run alembic stamp 3b7a1d2e4f56  # Use a valid revision

# Option B: Clear version table and re-run
psql "$DATABASE_URL" -c "DELETE FROM habits.alembic_version;"
poetry run alembic upgrade head
```

### Issue 3: "ImportError: cannot import name 'Base'"

**Error:**
```python
ImportError: cannot import name 'Base' from 'practices.repository.models'
```

**Cause:** env.py can't find models

**Solution:**
```python
# In alembic/env.py, ensure correct import:
from practices.repository.database import Base  # NOT models

# Or add to sys.path:
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Issue 4: "Multiple heads detected"

**Error:**
```
alembic.util.exc.CommandError: Multiple heads are present; please specify a target revision.
```

**Cause:** Migration history has branches (two migrations from same parent)

**Solution:**
```bash
# Show heads
poetry run alembic heads

# Merge heads
poetry run alembic merge -m "merge heads" abc123 def456
poetry run alembic upgrade head
```

---

## Environment Variables

**Required for all Alembic commands:**

```bash
# Production Supabase
export DATABASE_URL="postgresql://postgres.xyz:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

# Or individual components
export DB_HOST="aws-0-us-east-1.pooler.supabase.com"
export DB_PORT="5432"
export DB_USER="postgres.xyz"
export DB_PASS="password"
export DB_NAME="postgres"

# Service will auto-construct DATABASE_URL from components
```

**Optional:**

```bash
# Force specific schema (overrides default)
export DB_SCHEMA="habits"

# Force specific driver
export DB_DRIVER="psycopg2"  # or "asyncpg"

# Environment selection (for src/alembic-config only)
export ALEMBIC_ENV="supabase"  # or "local"
```

---

## Next Steps

1. ✅ Review this document (you are here)
2. ⏭️ Fix meals_service deprecated API
3. ⏭️ Create practices_service Alembic config
4. ⏭️ Create users_service Alembic config
5. ⏭️ Test 2 services manually (habits + movements)
6. ⏭️ Run orchestration script (03-run-migrations.sh)
7. ⏭️ Test new configs (practices + users)
8. ⏭️ Verify all schemas in database

---

## Reference: Alembic Directory Structure

```
service_name/
├── alembic/
│   ├── env.py                    # ← Migration runtime environment
│   ├── script.py.mako            # ← Migration file template
│   ├── README                    # ← Auto-generated docs
│   └── versions/                 # ← Migration files (chronological)
│       ├── __init__.py
│       ├── abc123_initial.py     # ← First migration
│       └── def456_add_col.py     # ← Second migration
├── alembic.ini                   # ← Alembic configuration
└── service_name/
    ├── repository/
    │   ├── database.py           # ← Base.metadata lives here
    │   └── models.py             # ← SQLAlchemy models
    └── web/
        └── config.py             # ← DATABASE_URL lives here
```

---

## Migration File Anatomy

```python
# alembic/versions/abc123_add_email.py

\"\"\"add email column

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-10-21 12:34:56

\"\"\"
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'abc123def456'
down_revision = 'previous_revision_id'  # ← Parent migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    \"\"\"Apply migration (forward).\"\"\"
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'])

def downgrade() -> None:
    \"\"\"Rollback migration (backward).\"\"\"
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'email')
```

---

## Ready to Proceed!

All existing configs reviewed. Ready to:
1. Create new configs for practices_service and users_service
2. Test manually
3. Run orchestration

Let me know when you're ready for the next step!
