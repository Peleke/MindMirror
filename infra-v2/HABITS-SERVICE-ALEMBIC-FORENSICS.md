# habits_service Alembic Forensic Analysis

**Date:** 2025-10-21
**Analyst:** DevOps (Alex - Staff Engineer Role)
**Objective:** Cross-check Alembic migrations against SQLAlchemy models FROM SCRATCH

---

## Executive Summary

🚨 **CRITICAL ISSUE FOUND:** Migration chain is broken - missing base migration

**Status:** ⚠️ **BROKEN** - Will likely fail on fresh database
**Recommended Action:** Create missing base migration or fix migration chain
**Estimated Fix Time:** 30-45 minutes

---

## Part 1: Staff Engineer Approach (How to Set Up Alembic)

### Given: habits_service SQLAlchemy Backend

**Discovery Phase:**

1. **Find the models** ✅
   ```bash
   find habits_service -name "*models*.py" -o -name "*tables*.py"

   Found:
   - habits_service/app/db/models.py (Base class)
   - habits_service/app/db/tables.py (actual table definitions)
   ```

2. **Understand the schema** ✅
   ```python
   # From models.py:
   class Base(DeclarativeBase):
       metadata = MetaData(schema=get_settings().database_schema)
   # Schema: "habits" (from settings)
   ```

3. **Count the tables** ✅
   ```python
   # From tables.py, found 16 tables:
   1. HabitTemplate
   2. LessonTemplate
   3. ProgramTemplate
   4. ProgramStepTemplate
   5. StepLessonTemplate
   6. LessonSegment
   7. StepDailyPlan
   8. UserProgramAssignment
   9. HabitEvent
   10. LessonEvent
   11. JournalTaskEvent
   12. LessonTask
   13. TemplateAccess
   14. TemplateProvenance
   ```

4. **Identify foreign keys** ✅
   ```python
   # Complex FK relationships:
   ProgramStepTemplate.program_template_id → ProgramTemplate.id
   StepLessonTemplate.program_step_template_id → ProgramStepTemplate.id
   UserProgramAssignment.program_template_id → ProgramTemplate.id
   # etc.
   ```

5. **Note special features** ✅
   - UUID primary keys (all tables)
   - Timestamps with `func.now()` server defaults
   - JSON columns (metadata, segments)
   - Unique constraints (composite keys)
   - Check constraints (permission, origin validation)
   - Partial indexes (e.g., program_templates.slug)
   - ondelete behaviors (RESTRICT, CASCADE, SET NULL)

---

### Staff Engineer Plan: Alembic Setup Steps

**Phase 1: Initialize Alembic**
```bash
cd habits_service
poetry run alembic init alembic
```

**Phase 2: Configure alembic.ini**
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@postgres:5432/swae
revision_environment = true  # Important for accessing settings
```

**Phase 3: Configure alembic/env.py**
```python
from habits_service.app.db.models import Base
from habits_service.app.config import get_settings

target_metadata = Base.metadata
DATABASE_SCHEMA = get_settings().database_schema  # "habits"

# Configure to use async engine + ensure schema exists
async def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL, poolclass=NullPool)
    async with connectable.connect() as connection:
        # CRITICAL: Create schema before migrations
        await connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DATABASE_SCHEMA}"))
        await connection.commit()

        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,  # CRITICAL
        version_table_schema=DATABASE_SCHEMA,  # CRITICAL
        compare_type=True,  # Detect type changes
    )
    with context.begin_transaction():
        context.run_migrations()
```

**Phase 4: Generate Initial Migration**
```bash
# This is THE MOST IMPORTANT STEP
poetry run alembic revision --autogenerate -m "initial schema - all 16 tables"

# Expected output:
# INFO  [alembic.autogenerate.compare] Detected added table 'habits.habit_templates'
# INFO  [alembic.autogenerate.compare] Detected added table 'habits.lesson_templates'
# ... (14 more)
# Generating /path/to/alembic/versions/abc123_initial_schema.py ... done
```

**Phase 5: Review Generated Migration**
```bash
cat alembic/versions/abc123_initial_schema.py

# Check for:
# 1. All 16 op.create_table() calls
# 2. All foreign keys specified
# 3. All indexes created
# 4. All unique constraints
# 5. All check constraints
# 6. schema='habits' on every operation
```

**Phase 6: Apply Migration**
```bash
poetry run alembic upgrade head

# Verify:
psql "$DATABASE_URL" -c "\dt habits.*"
# Should show all 16 tables + alembic_version
```

**Phase 7: Lock It Down**
```bash
# Add environment guard to init_db()
# (covered in separate task)
```

---

## Part 2: Actual Walk-Through FROM SCRATCH

Let me simulate creating this from scratch to see what SHOULD exist:

### Step 1: Run autogenerate against clean database

**Hypothetical command:**
```bash
# Assume fresh database with no habits schema
cd habits_service
export DATABASE_URL="postgresql://user:pass@host:5432/swae"
poetry run alembic revision --autogenerate -m "initial schema"
```

**What Alembic SHOULD detect:**

```python
# Expected operations (from comparing Base.metadata to empty DB):

# 1. Create schema
op.execute("CREATE SCHEMA IF NOT EXISTS habits")

# 2. Create all 16 tables in dependency order
op.create_table('habit_templates',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    # ... all columns ...
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug'),
    schema='habits'
)

op.create_table('lesson_templates', ...)
op.create_table('program_templates', ...)

# 3. Create tables with FKs (dependency order)
op.create_table('program_step_templates',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('program_template_id', postgresql.UUID(), nullable=False),
    sa.Column('habit_template_id', postgresql.UUID(), nullable=True),
    # ...
    sa.ForeignKeyConstraint(['program_template_id'], ['habits.program_templates.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['habit_template_id'], ['habits.habit_templates.id'], ondelete='RESTRICT'),
    schema='habits'
)

# ... etc for all tables ...

# 4. Create indexes
op.create_index(op.f('ix_habit_templates_slug'), 'habit_templates', ['slug'], schema='habits')
# ... etc ...

# 5. Create composite unique constraints (if not in create_table)
# Usually handled in create_table with UniqueConstraint
```

**Expected file structure:**
```python
"""initial schema - all 16 tables

Revision ID: abc123def456
Revises:
Create Date: 2025-10-21 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'abc123def456'
down_revision = None  # ← First migration, no parent
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Schema creation
    op.execute("CREATE SCHEMA IF NOT EXISTS habits")

    # Create base tables (no FKs)
    op.create_table('habit_templates', ...)
    op.create_table('lesson_templates', ...)
    op.create_table('program_templates', ...)

    # Create tables with FKs (dependency order)
    op.create_table('program_step_templates', ...)
    op.create_table('step_lesson_templates', ...)
    # ... etc ...

    # Create indexes
    op.create_index(...)
    # ... etc ...

def downgrade() -> None:
    # Drop in reverse order
    op.drop_index(...)
    op.drop_table('lesson_tasks', schema='habits')
    # ...
    op.drop_table('program_templates', schema='habits')
    op.drop_table('lesson_templates', schema='habits')
    op.drop_table('habit_templates', schema='habits')

    # Optionally drop schema
    # op.execute("DROP SCHEMA IF EXISTS habits CASCADE")
```

---

## Part 3: Cross-Check Against Existing Migrations

### What ACTUALLY Exists

**Files:**
```
alembic/versions/
├── 189b1231afd4_bootstrap_tables.py
└── 3b7a1d2e4f56_soft_delete_program_templates.py
```

**Migration chain (from file contents):**
```python
# File: 189b1231afd4_bootstrap_tables.py
revision = '2a3f4c9d1cde'  # ← MISMATCH! Filename says 189b, content says 2a3f
down_revision = '189b1231afd4'  # ← This revision doesn't exist in any file!

# File: 3b7a1d2e4f56_soft_delete_program_templates.py
revision = '3b7a1d2e4f56'  # ← OK, matches filename
down_revision = '2a3f4c9d1cde'  # ← OK, references previous migration
```

**Logical chain:**
```
<base> → '189b1231afd4' → '2a3f4c9d1cde' → '3b7a1d2e4f56'
           ^^^^^^^^^^^^     ^^^^^^^^^^^^     ^^^^^^^^^^^^
           MISSING FILE!    File: 189b1...    File: 3b7a...
```

**What each migration does:**

#### Migration '2a3f4c9d1cde' (file: 189b1231afd4_bootstrap_tables.py)
```python
def upgrade() -> None:
    # Changes FK constraints to CASCADE/RESTRICT
    # Assumes tables already exist!

    ALTER TABLE habits.program_step_templates
    DROP CONSTRAINT IF EXISTS program_step_templates_program_template_id_fkey;

    ALTER TABLE habits.program_step_templates
    ADD CONSTRAINT program_step_templates_program_template_id_fkey
    FOREIGN KEY (program_template_id)
    REFERENCES habits.program_templates(id)
    ON DELETE CASCADE;  # ← Changed from RESTRICT

    # Same for:
    # - step_lesson_templates (CASCADE)
    # - user_program_assignments (RESTRICT explicit)
```

**Problem:** This migration modifies FK constraints but doesn't create the tables!

#### Migration '3b7a1d2e4f56' (file: 3b7a1d2e4f56_soft_delete_program_templates.py)
```python
def upgrade() -> None:
    # 1) Add is_deleted column to program_templates
    ALTER TABLE habits.program_templates
    ADD COLUMN IF NOT EXISTS is_deleted boolean NOT NULL DEFAULT false;

    # 2) Create partial unique index
    CREATE UNIQUE INDEX program_templates_title_active_idx
    ON habits.program_templates (title)
    WHERE is_deleted = false;

    # 3) Create trigger function to prevent assigning deleted programs
    CREATE OR REPLACE FUNCTION habits.prevent_assign_to_deleted() ...

    # 4) Create trigger
    CREATE TRIGGER trg_prevent_assign_deleted_program ...

    # 5) Create helper function
    CREATE OR REPLACE FUNCTION habits.archive_program_template(p_id uuid) ...
```

**Problem:** This assumes `program_templates` table exists!

---

## Part 4: The Gap Analysis

### 🚨 **CRITICAL ISSUES FOUND**

#### Issue 1: Missing Base Migration (Revision '189b1231afd4')

**Expected:**
- File: `189b1231afd4_*.py` with `revision = '189b1231afd4'` and `down_revision = None`
- Should create all 16 tables with base schema

**Actual:**
- No file contains `revision = '189b1231afd4'`
- Migration '2a3f4c9d1cde' references it as parent (`down_revision = '189b1231afd4'`)
- **Result:** Broken chain, Alembic will error

#### Issue 2: Filename vs Content Mismatch

**File:** `189b1231afd4_bootstrap_tables.py`
**Content:** `revision = '2a3f4c9d1cde'`

**Why this is confusing but not fatal:**
- Alembic reads revision IDs from file content, not filename
- Filename is just for human sorting/organization
- But indicates someone renamed/edited file incorrectly

#### Issue 3: Missing Table Creation

**Current migrations assume tables exist:**
- Migration '2a3f4c9d1cde': Modifies FK constraints (assumes tables exist)
- Migration '3b7a1d2e4f56': Adds columns/triggers (assumes tables exist)

**But no migration creates the tables!**

Likely scenarios:
1. **Scenario A:** Missing migration was deleted/lost
2. **Scenario B:** Tables were created manually with `Base.metadata.create_all()`
3. **Scenario C:** Missing migration exists elsewhere (git history, old branch)

---

## Part 5: Diagnosis

### Root Cause Analysis

**What probably happened:**

1. **Initial setup (June/July):**
   - Developer ran `alembic init alembic`
   - Created initial migration: `alembic revision --autogenerate -m "bootstrap tables"`
   - Alembic generated file: `189b1231afd4_bootstrap_tables.py`
   - Content had `revision = '189b1231afd4'`, `down_revision = None`
   - This migration created all 16 tables

2. **Subsequent changes (August):**
   - Developer wanted to add CASCADE deletes
   - Ran `alembic revision --autogenerate -m "add cascade deletes"`
   - Alembic generated: `2a3f4c9d1cde_add_cascade_deletes.py`
   - Content: `revision = '2a3f4c9d1cde'`, `down_revision = '189b1231afd4'`

3. **File mishap (September 17):**
   - Someone **accidentally overwrote** `189b1231afd4_bootstrap_tables.py`
   - Replaced its content with the CASCADE migration content
   - Lost the original table creation migration
   - Filename stayed as `189b1231afd4_bootstrap_tables.py`
   - Content became revision '2a3f4c9d1cde'

**Evidence:**
- File modified date: September 17, 2025
- File name doesn't match content revision
- Migration chain references non-existent revision

---

## Part 6: Impact Assessment

### What Breaks

**Scenario 1: Fresh Database**
```bash
cd habits_service
export DATABASE_URL="postgresql://user:pass@host:5432/new_db"
poetry run alembic upgrade head

# ERROR:
# alembic.util.exc.CommandError: Can't locate revision identified by '189b1231afd4'
```

**Why:** Alembic tries to find migration '189b1231afd4' (referenced as parent) but no file contains it.

**Scenario 2: Existing Database (Development)**
```bash
# If database was created with Base.metadata.create_all()
psql $DATABASE_URL -c "SELECT * FROM habits.alembic_version"
# Returns: (empty or doesn't exist)

poetry run alembic upgrade head
# Might work if Alembic stamps version, but fragile
```

**Scenario 3: Production Deployment**
```bash
cd infra-v2/bootstrap
./03-run-migrations.sh  # Orchestration script

# FAILS on habits_service with:
# Can't locate revision '189b1231afd4'
```

---

## Part 7: The Fix

### Option A: Reconstruct Missing Migration (Recommended)

**Create the base migration that SHOULD have existed:**

```bash
cd habits_service

# Create manual migration (no autogenerate, since tables might already exist)
poetry run alembic revision -m "bootstrap tables - base schema"

# This creates: abc123_bootstrap_tables.py
# Edit it manually:
```

```python
"""bootstrap tables - base schema

Revision ID: 189b1231afd4  # ← Use the missing revision ID
Revises:
Create Date: 2025-06-01 00:00:00  # ← Backdate to before other migrations

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '189b1231afd4'  # ← The missing revision
down_revision = None  # ← First migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create schema
    op.execute("CREATE SCHEMA IF NOT EXISTS habits")

    # Create all tables
    # (Copy from current SQLAlchemy models or reconstruct)

    # Base tables (no FKs)
    op.create_table('habit_templates',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('hero_image_url', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('default_duration_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        schema='habits'
    )

    # ... repeat for all 16 tables ...
    # (This is tedious but necessary)

def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('lesson_tasks', schema='habits')
    # ... etc ...
    op.drop_table('habit_templates', schema='habits')
```

**Save as:** `alembic/versions/189b1231afd4_bootstrap_tables_RECONSTRUCTED.py`

**Test:**
```bash
# Rename old file
mv alembic/versions/189b1231afd4_bootstrap_tables.py alembic/versions/2a3f4c9d1cde_add_cascade_deletes.py

# Put reconstructed file
mv alembic/versions/189b1231afd4_bootstrap_tables_RECONSTRUCTED.py alembic/versions/189b1231afd4_bootstrap_tables.py

# Test migration chain
poetry run alembic history
# Should show:
# <base> -> 189b1231afd4, bootstrap tables - base schema
# 189b1231afd4 -> 2a3f4c9d1cde, add cascade deletes
# 2a3f4c9d1cde -> 3b7a1d2e4f56, soft delete for program_templates

# Test on fresh DB
poetry run alembic upgrade head
```

---

### Option B: Squash and Start Fresh (Nuclear Option)

**Only if databases can be wiped:**

```bash
cd habits_service

# Delete all migrations
rm alembic/versions/*.py
# Keep __init__.py

# Generate fresh migration from current models
poetry run alembic revision --autogenerate -m "initial schema - consolidated"

# Review generated file (should have all 16 tables)
cat alembic/versions/NEWID_initial_schema.py

# Apply
poetry run alembic upgrade head
```

**Pros:** Clean, matches current models exactly
**Cons:** Loses migration history, requires database wipe

---

### Option C: Quick Fix with Stamp (Hacky, Not Recommended)

**If you just need to unblock testing:**

```bash
# Edit 2a3f4c9d1cde migration
# Change:
down_revision = '189b1231afd4'
# To:
down_revision = None

# Now chain is:
# <base> -> 2a3f4c9d1cde -> 3b7a1d2e4f56

# But this assumes tables already exist from Base.metadata.create_all()
```

**Pros:** Quick
**Cons:** Migration history is lie, won't work on fresh DB

---

## Part 8: Recommended Action Plan

### For Immediate Production Deployment

**Choice:** **Option A** (Reconstruct Missing Migration)

**Steps:**

1. **Backup current migrations:**
   ```bash
   cp -r habits_service/alembic/versions habits_service/alembic/versions.backup
   ```

2. **Reconstruct base migration '189b1231afd4':**
   - Create file manually
   - Copy table definitions from current SQLAlchemy models
   - Use revision ID '189b1231afd4', down_revision None
   - Include all 16 tables

3. **Rename mislabeled migration:**
   ```bash
   mv alembic/versions/189b1231afd4_bootstrap_tables.py \
      alembic/versions/2a3f4c9d1cde_add_cascade_deletes.py
   ```

4. **Test migration chain:**
   ```bash
   poetry run alembic history  # Verify chain
   ```

5. **Test on fresh database:**
   ```bash
   # Spin up temp database
   docker run -d --name test-pg -e POSTGRES_PASSWORD=test -p 5555:5432 postgres:15

   export DATABASE_URL="postgresql://postgres:test@localhost:5555/postgres"
   poetry run alembic upgrade head

   # Verify all tables created
   psql "$DATABASE_URL" -c "\dt habits.*"

   # Clean up
   docker stop test-pg && docker rm test-pg
   ```

6. **Commit fixed migrations:**
   ```bash
   git add alembic/versions/
   git commit -m "fix(habits): reconstruct missing base migration 189b1231afd4"
   ```

---

## Part 9: Conclusion

### Summary of Findings

✅ **SQLAlchemy Models:** Well-defined, 16 tables, complex relationships
❌ **Alembic Migrations:** Broken chain, missing base migration
⚠️ **Current State:** Works if tables created via metadata.create_all(), will FAIL on fresh DB
🔧 **Fix Required:** Reconstruct missing migration '189b1231afd4'

### Staff Engineer Assessment

**Grade: D+ (Works by accident, not by design)**

**Why it (probably) works now:**
- Development uses `Base.metadata.create_all()` to create tables
- Migrations never ran on empty database
- Team hasn't tested fresh database deployment

**Why it will break in production:**
- Script 03 (migration orchestration) expects clean migration path
- Fresh database → Alembic can't find revision '189b1231afd4' → FAIL
- No fallback to metadata.create_all() in production

**Professional Standard:**
- Migrations should work on empty database
- Migration chain should be complete
- Filename should match content revision
- No reliance on metadata.create_all() in production

---

## Appendix: Quick Reference

### Current State
```
Files (2):
  - 189b1231afd4_bootstrap_tables.py (contains '2a3f4c9d1cde')
  - 3b7a1d2e4f56_soft_delete_program_templates.py (contains '3b7a1d2e4f56')

Chain:
  <base> → '189b1231afd4' → '2a3f4c9d1cde' → '3b7a1d2e4f56'
             ^^^^^^^^^^^
             MISSING!
```

### Should Be
```
Files (3):
  - 189b1231afd4_bootstrap_tables.py (contains '189b1231afd4', down_revision=None)
  - 2a3f4c9d1cde_add_cascade_deletes.py (contains '2a3f4c9d1cde', down_revision='189b')
  - 3b7a1d2e4f56_soft_delete_program_templates.py (contains '3b7a1d2e4f56', down_revision='2a3f')

Chain:
  <base> → '189b1231afd4' → '2a3f4c9d1cde' → '3b7a1d2e4f56'
           ✅ Creates       ✅ Modifies FK   ✅ Adds soft
              tables           constraints       delete
```

---

**Next Action:** Choose fix option (recommend Option A) and implement before running script 03.
