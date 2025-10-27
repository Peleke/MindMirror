# Alembic End-to-End Walkthrough (habits_service)

**Goal:** Complete step-by-step guide to running Alembic migrations
**Audience:** Someone who's done this before but needs a refresher
**Example Service:** habits_service (has 2 migrations already)

---

## The Setup: What We're Working With

### Files in habits_service

```
habits_service/
├── alembic.ini                              # Configuration file
├── alembic/
│   ├── env.py                              # Migration runtime environment
│   ├── script.py.mako                      # Template for new migrations
│   └── versions/                           # Migration files (chronological)
│       ├── 189b1231afd4_bootstrap_tables.py       # Migration #1
│       └── 3b7a1d2e4f56_soft_delete_program_templates.py  # Migration #2
└── habits_service/
    └── app/
        └── db/
            ├── models.py                    # SQLAlchemy models (Base.metadata)
            └── tables.py                    # Table definitions
```

### Migration Chain

```
<base> → 189b1231afd4 → 2a3f4c9d1cde → 3b7a1d2e4f56 (head)
         (bootstrap)    (cascades)      (soft delete)
```

**Note:** Filename prefixes (189b, 3b7a) are just for sorting. The real IDs are inside the files (revision = '2a3f4c9d1cde', etc.).

---

## Phase 1: Check Current State (Before Any Migrations)

### Command 1: `alembic current`

**What you run:**
```bash
cd habits_service
export DATABASE_URL="postgresql://user:pass@host:5432/swae"
poetry run alembic current
```

**What happens under the hood:**

1. **Alembic reads alembic.ini:**
   ```ini
   [alembic]
   script_location = alembic
   sqlalchemy.url = postgresql+asyncpg://...  # Overridden by DATABASE_URL env var
   ```

2. **Alembic runs alembic/env.py:**
   ```python
   # env.py line 64-78:
   async def run_migrations_online():
       connectable = create_async_engine(DATABASE_URL, poolclass=NullPool)
       async with connectable.connect() as connection:
           # Opens connection to database
   ```

3. **Alembic queries the database:**
   ```sql
   SELECT version_num FROM habits.alembic_version LIMIT 1;
   ```

4. **What you see (if fresh database):**
   ```
   INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
   INFO  [alembic.runtime.migration] Will assume transactional DDL.
   ```
   *No output = no migrations applied yet*

5. **What you see (if migrations already applied):**
   ```
   INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
   INFO  [alembic.runtime.migration] Will assume transactional DDL.
   3b7a1d2e4f56 (head)
   ```

**Pragmatically:**
- Quick way to check: "Have I run migrations yet?"
- Like `git log --oneline -1` for your database schema

---

### Command 2: `alembic history`

**What you run:**
```bash
poetry run alembic history
```

**What happens under the hood:**

1. **Alembic scans alembic/versions/ directory:**
   ```python
   # Finds all .py files
   files = [
       '189b1231afd4_bootstrap_tables.py',
       '3b7a1d2e4f56_soft_delete_program_templates.py'
   ]
   ```

2. **Alembic reads each migration file's header:**
   ```python
   # From 189b1231afd4_bootstrap_tables.py:
   revision = '2a3f4c9d1cde'
   down_revision = '189b1231afd4'

   # From 3b7a1d2e4f56_soft_delete_program_templates.py:
   revision = '3b7a1d2e4f56'
   down_revision = '2a3f4c9d1cde'
   ```

3. **Alembic builds migration chain:**
   ```python
   # Creates linked list:
   <base> → 189b1231afd4 → 2a3f4c9d1cde → 3b7a1d2e4f56 (head)
   ```

4. **What you see:**
   ```
   189b1231afd4 -> 2a3f4c9d1cde, add cascade deletes for program templates
   2a3f4c9d1cde -> 3b7a1d2e4f56 (head), soft delete for program_templates
   <base> -> 189b1231afd4, bootstrap tables
   ```

**Pragmatically:**
- Shows all available migrations
- `(head)` marks the latest
- Like `git log --oneline` for schema changes

---

## Phase 2: Apply Migrations

### Command 3: `alembic upgrade head`

**What you run:**
```bash
poetry run alembic upgrade head
```

**What happens under the hood (step-by-step):**

#### Step 1: Calculate Migration Path

```python
# Alembic:
current_revision = SELECT version_num FROM habits.alembic_version
# Returns: None (table doesn't exist yet)

target_revision = "head" = "3b7a1d2e4f56" (latest)

# Calculate path from current to target:
path = [
    '189b1231afd4',  # bootstrap_tables
    '2a3f4c9d1cde',  # cascade deletes
    '3b7a1d2e4f56',  # soft delete
]
```

#### Step 2: Begin Transaction

```sql
BEGIN;
-- All migrations run inside this transaction
-- Either ALL succeed or ALL rollback
```

#### Step 3: Create alembic_version Table (First Time Only)

```sql
CREATE TABLE habits.alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
```

#### Step 4: Run Migration #1 (189b1231afd4)

**Python:**
```python
# Alembic calls upgrade() from 189b1231afd4_bootstrap_tables.py
def upgrade() -> None:
    op.execute("""
        ALTER TABLE habits.program_step_templates
        DROP CONSTRAINT IF EXISTS program_step_templates_program_template_id_fkey;
        ...
    """)
```

**SQL executed:**
```sql
-- Creates tables (from earlier bootstrap migration)
CREATE TABLE habits.program_templates (...);
CREATE TABLE habits.program_step_templates (...);
-- etc.
```

**What you see:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 189b1231afd4, bootstrap tables
```

**Database state after this step:**
```
habits schema:
  - program_templates (table)
  - program_step_templates (table)
  - step_lesson_templates (table)
  - user_program_assignments (table)
  - alembic_version (table) → version_num = '189b1231afd4'
```

#### Step 5: Run Migration #2 (2a3f4c9d1cde)

**Python:**
```python
# Alembic calls upgrade() from next migration in chain
def upgrade() -> None:
    # Add CASCADE to foreign keys
    op.execute("""
        ALTER TABLE habits.program_step_templates
        DROP CONSTRAINT IF EXISTS program_step_templates_program_template_id_fkey;
        ALTER TABLE habits.program_step_templates
        ADD CONSTRAINT program_step_templates_program_template_id_fkey
        FOREIGN KEY (program_template_id)
        REFERENCES habits.program_templates(id)
        ON DELETE CASCADE;
    """)
```

**SQL executed:**
```sql
-- Modifies foreign key constraints
ALTER TABLE habits.program_step_templates DROP CONSTRAINT ...;
ALTER TABLE habits.program_step_templates ADD CONSTRAINT ... ON DELETE CASCADE;
-- (same for step_lesson_templates)
-- (and user_program_assignments with RESTRICT)
```

**What you see:**
```
INFO  [alembic.runtime.migration] Running upgrade 189b1231afd4 -> 2a3f4c9d1cde, add cascade deletes
```

**Database state after this step:**
```
habits schema:
  - program_templates (table) ← same
  - program_step_templates (table) ← FK now has ON DELETE CASCADE
  - step_lesson_templates (table) ← FK now has ON DELETE CASCADE
  - user_program_assignments (table) ← FK now has ON DELETE RESTRICT
  - alembic_version → version_num = '2a3f4c9d1cde'
```

#### Step 6: Run Migration #3 (3b7a1d2e4f56)

**Python:**
```python
def upgrade() -> None:
    # 1) Add is_deleted column
    op.execute("""
        ALTER TABLE habits.program_templates
        ADD COLUMN IF NOT EXISTS is_deleted boolean NOT NULL DEFAULT false;
    """)

    # 2) Create partial unique index
    op.execute("""
        CREATE UNIQUE INDEX program_templates_title_active_idx
        ON habits.program_templates (title)
        WHERE is_deleted = false;
    """)

    # 3) Create trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION habits.prevent_assign_to_deleted()
        RETURNS trigger AS $$ ... $$;
    """)

    # 4) Create trigger
    op.execute("""
        CREATE TRIGGER trg_prevent_assign_deleted_program
        BEFORE INSERT OR UPDATE ON habits.user_program_assignments
        FOR EACH ROW EXECUTE FUNCTION habits.prevent_assign_to_deleted();
    """)

    # 5) Create helper function
    op.execute("""
        CREATE OR REPLACE FUNCTION habits.archive_program_template(p_id uuid) ...;
    """)
```

**SQL executed:**
```sql
-- Add column
ALTER TABLE habits.program_templates ADD COLUMN is_deleted boolean NOT NULL DEFAULT false;

-- Create partial unique index (only for non-deleted rows)
CREATE UNIQUE INDEX program_templates_title_active_idx
ON habits.program_templates (title)
WHERE is_deleted = false;

-- Create trigger function
CREATE OR REPLACE FUNCTION habits.prevent_assign_to_deleted() ...;

-- Create trigger
CREATE TRIGGER trg_prevent_assign_deleted_program ...;

-- Create helper function
CREATE OR REPLACE FUNCTION habits.archive_program_template(p_id uuid) ...;
```

**What you see:**
```
INFO  [alembic.runtime.migration] Running upgrade 2a3f4c9d1cde -> 3b7a1d2e4f56, soft delete for program_templates
```

**Database state after this step:**
```
habits schema:
  - program_templates (table)
      ↳ NEW COLUMN: is_deleted boolean DEFAULT false
      ↳ NEW INDEX: program_templates_title_active_idx (partial)
  - program_step_templates (table)
  - step_lesson_templates (table)
  - user_program_assignments (table)
      ↳ NEW TRIGGER: trg_prevent_assign_deleted_program
  - NEW FUNCTION: prevent_assign_to_deleted()
  - NEW FUNCTION: archive_program_template(uuid)
  - alembic_version → version_num = '3b7a1d2e4f56'
```

#### Step 7: Commit Transaction

```sql
COMMIT;
-- All changes permanent
```

**What you see (final output):**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 189b1231afd4, bootstrap tables
INFO  [alembic.runtime.migration] Running upgrade 189b1231afd4 -> 2a3f4c9d1cde, add cascade deletes
INFO  [alembic.runtime.migration] Running upgrade 2a3f4c9d1cde -> 3b7a1d2e4f56, soft delete for program_templates
```

**Pragmatically:**
- All 3 migrations ran in sequence
- If ANY migration failed, entire transaction would rollback
- Database is now at "head" (latest schema)

---

## Phase 3: Verify Migrations Applied

### Command 4: `alembic current` (again)

**What you run:**
```bash
poetry run alembic current
```

**What happens:**
```sql
SELECT version_num FROM habits.alembic_version LIMIT 1;
-- Returns: '3b7a1d2e4f56'
```

**What you see:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
3b7a1d2e4f56 (head)
```

**Pragmatically:**
- Confirms we're at the latest revision
- `(head)` means no pending migrations

---

## Phase 4: Test Idempotency (Run Again)

### Command 5: `alembic upgrade head` (second time)

**What you run:**
```bash
poetry run alembic upgrade head
```

**What happens under the hood:**

```python
# Alembic:
current_revision = SELECT version_num FROM habits.alembic_version
# Returns: '3b7a1d2e4f56'

target_revision = "head" = '3b7a1d2e4f56'

# Calculate path:
if current_revision == target_revision:
    print("Already at target revision")
    path = []  # No migrations to run
else:
    path = calculate_upgrade_path(current, target)
```

**What you see:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```
*(No "Running upgrade..." messages)*

**Pragmatically:**
- Running `upgrade head` multiple times is safe
- Alembic checks current version, only runs missing migrations
- This is why the orchestration script can run all services without duplicating work

---

## Phase 5: Create a New Migration

### Command 6: `alembic revision --autogenerate -m "add email to program templates"`

**What you run:**
```bash
poetry run alembic revision --autogenerate -m "add email to program templates"
```

**What happens under the hood:**

#### Step 1: Load Current Database Schema

```python
# Alembic connects to database
connection = create_async_engine(DATABASE_URL).connect()

# Inspects current schema
db_schema = inspector.get_columns('program_templates', schema='habits')
# Returns:
# [
#   {'name': 'id', 'type': UUID(), ...},
#   {'name': 'title', 'type': String(), ...},
#   {'name': 'is_deleted', 'type': Boolean(), ...},
#   # etc.
# ]
```

#### Step 2: Load Target Metadata (from SQLAlchemy Models)

```python
# Alembic imports your models
from habits_service.app.db.models import Base

# Gets metadata
target_metadata = Base.metadata

# For program_templates table:
model_columns = [
    Column('id', UUID(), ...),
    Column('title', String(), ...),
    Column('is_deleted', Boolean(), ...),
    Column('email', String(), ...),  # ← NEW in model!
]
```

#### Step 3: Compare Database vs Models (Autogenerate Magic!)

```python
# Alembic compares:
db_columns = {'id', 'title', 'is_deleted'}
model_columns = {'id', 'title', 'is_deleted', 'email'}

# Detects difference:
added_columns = model_columns - db_columns  # {'email'}
removed_columns = db_columns - model_columns  # {}
modified_columns = detect_type_changes()  # {}

# Generates migration operations:
operations = [
    op.add_column('program_templates',
                  sa.Column('email', sa.String(), nullable=True),
                  schema='habits')
]
```

#### Step 4: Generate Migration File

```python
# Alembic creates new file:
filename = f"alembic/versions/{generate_id()}_add_email_to_program_templates.py"
# Example: abc123def456_add_email_to_program_templates.py

# Fills in template from script.py.mako:
revision_id = 'abc123def456'
down_revision = '3b7a1d2e4f56'  # Current head

# Writes file with detected operations
```

**What you see:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'habits.program_templates.email'
  Generating /path/to/alembic/versions/abc123def456_add_email_to_program_templates.py ...  done
```

**Generated file (abc123def456_add_email_to_program_templates.py):**
```python
"""add email to program templates

Revision ID: abc123def456
Revises: 3b7a1d2e4f56
Create Date: 2025-10-21 14:30:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123def456'
down_revision = '3b7a1d2e4f56'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('program_templates',
                  sa.Column('email', sa.String(), nullable=True),
                  schema='habits')

def downgrade() -> None:
    op.drop_column('program_templates', 'email', schema='habits')
```

**Pragmatically:**
- Alembic auto-detected model change
- Generated migration file with upgrade + downgrade
- **ALWAYS REVIEW THIS FILE** before applying!
  - Autogenerate isn't perfect
  - Might miss renames (sees drop + add)
  - Might miss data migrations

---

### Command 7: Review Generated Migration

**What you run:**
```bash
cat alembic/versions/abc123def456_add_email_to_program_templates.py
```

**What to check:**
1. **upgrade() looks correct** - Does what you intended?
2. **downgrade() is reversible** - Can you undo this?
3. **No data loss** - Adding nullable column (safe), or need DEFAULT value?
4. **Schema correct** - `schema='habits'` specified?

**Common fixes:**

```python
# BAD: Adds NOT NULL column without DEFAULT
op.add_column('program_templates',
              sa.Column('email', sa.String(), nullable=False))  # ← FAILS if table has rows!

# GOOD: Adds nullable first, then backfill, then set NOT NULL
op.add_column('program_templates',
              sa.Column('email', sa.String(), nullable=True))  # ← Safe
op.execute("UPDATE habits.program_templates SET email = '' WHERE email IS NULL")  # ← Backfill
op.alter_column('program_templates', 'email', nullable=False, schema='habits')  # ← Now safe
```

**If migration is wrong:**
```bash
# Delete generated file
rm alembic/versions/abc123def456_add_email_to_program_templates.py

# Fix your models or create manual migration
poetry run alembic revision -m "add email to program templates"  # Manual (no --autogenerate)

# Edit the file manually
vim alembic/versions/new_id_add_email_to_program_templates.py
```

---

### Command 8: Apply New Migration

**What you run:**
```bash
poetry run alembic upgrade head
```

**What happens:**

```python
# Alembic:
current = '3b7a1d2e4f56'
target = 'abc123def456'  # New head

path = ['abc123def456']  # Only one migration to run
```

**SQL executed:**
```sql
BEGIN;

-- Run upgrade() from abc123def456_add_email_to_program_templates.py
ALTER TABLE habits.program_templates
ADD COLUMN email VARCHAR NULL;

-- Update version
UPDATE habits.alembic_version
SET version_num = 'abc123def456';

COMMIT;
```

**What you see:**
```
INFO  [alembic.runtime.migration] Running upgrade 3b7a1d2e4f56 -> abc123def456, add email to program templates
```

**Database state:**
```
habits.program_templates:
  - id (uuid)
  - title (varchar)
  - is_deleted (boolean)
  - email (varchar) ← NEW!

habits.alembic_version:
  - version_num = 'abc123def456'
```

---

## Phase 6: Rollback a Migration

### Command 9: `alembic downgrade -1`

**What you run:**
```bash
poetry run alembic downgrade -1
```

**What happens:**

```python
# Alembic:
current = 'abc123def456'
target = '-1' = '3b7a1d2e4f56'  # One step back

path = ['abc123def456']  # Migration to undo

# Calls downgrade() instead of upgrade()
```

**SQL executed:**
```sql
BEGIN;

-- Run downgrade() from abc123def456_add_email_to_program_templates.py
ALTER TABLE habits.program_templates
DROP COLUMN email;

-- Update version (go backwards)
UPDATE habits.alembic_version
SET version_num = '3b7a1d2e4f56';

COMMIT;
```

**What you see:**
```
INFO  [alembic.runtime.migration] Running downgrade abc123def456 -> 3b7a1d2e4f56,
```

**Database state:**
```
habits.program_templates:
  - id (uuid)
  - title (varchar)
  - is_deleted (boolean)
  - email (GONE!)

habits.alembic_version:
  - version_num = '3b7a1d2e4f56'
```

**Pragmatically:**
- Rolled back one migration
- Data in `email` column is **LOST** (column dropped)
- Can run `upgrade head` again to re-apply

---

## Common Workflows Summary

### Workflow 1: Fresh Database Setup
```bash
# 1. Check status (should be empty)
poetry run alembic current

# 2. Apply all migrations
poetry run alembic upgrade head

# 3. Verify
poetry run alembic current  # Should show (head)
```

### Workflow 2: Adding a Feature (New Column)
```bash
# 1. Update SQLAlchemy model
# Edit habits_service/app/db/models.py
# Add: email = Column(String)

# 2. Generate migration
poetry run alembic revision --autogenerate -m "add email column"

# 3. Review generated migration
cat alembic/versions/XXXXX_add_email_column.py

# 4. Apply migration
poetry run alembic upgrade head

# 5. Verify
poetry run alembic current
```

### Workflow 3: Fixing a Bad Migration
```bash
# 1. Rollback bad migration
poetry run alembic downgrade -1

# 2. Delete migration file
rm alembic/versions/bad_migration.py

# 3. Regenerate (after fixing models)
poetry run alembic revision --autogenerate -m "corrected migration"

# 4. Apply
poetry run alembic upgrade head
```

### Workflow 4: Production Deployment
```bash
# 1. Check current version
poetry run alembic current

# 2. Dry-run (see SQL without executing)
poetry run alembic upgrade head --sql

# 3. Apply migrations
poetry run alembic upgrade head

# 4. Verify
poetry run alembic current
psql "$DATABASE_URL" -c "\dt habits.*"
```

---

## Key Concepts

### Revision IDs
- **Unique identifier** for each migration (e.g., `3b7a1d2e4f56`)
- Generated by Alembic (usually first 12 chars of timestamp hash)
- **File names don't matter** - Alembic reads IDs from inside files
- Example: File `189b1231afd4_bootstrap.py` might have `revision = '2a3f4c9d1cde'`

### Migration Chain
- Linked list: Each migration has `down_revision` pointing to parent
- `<base>` = starting point (no migrations)
- `(head)` = latest migration
- Alembic calculates shortest path from current to target

### Transactional DDL
- All migrations run in single transaction
- **PostgreSQL advantage**: Can rollback DDL (CREATE TABLE, etc.)
- If migration #2 fails, migration #1 is also rolled back
- MySQL can't do this (DDL commits immediately)

### Autogenerate Limitations
- Detects: added/removed tables, columns, indexes, foreign keys
- Doesn't detect: renamed columns (sees drop + add), data changes, custom constraints
- **Always review generated migrations!**

### Idempotency
- Running `upgrade head` multiple times is safe
- Alembic checks `alembic_version` table first
- Only runs migrations not yet applied
- This is why orchestration scripts work

---

## Pro Tips

1. **Always use --autogenerate for schema changes**
   - Faster than writing by hand
   - Catches things you might forget

2. **But always review the generated file**
   - Autogenerate isn't perfect
   - Might need manual tweaks

3. **Use meaningful migration messages**
   - Good: `"add email column to program templates"`
   - Bad: `"update"`, `"fix"`, `"changes"`

4. **Test downgrade() before deploying**
   ```bash
   alembic upgrade +1   # Apply
   alembic downgrade -1  # Undo
   alembic upgrade head  # Re-apply
   ```

5. **Use --sql for production preview**
   ```bash
   alembic upgrade head --sql > migration.sql
   # Review SQL before running on production
   ```

6. **One logical change per migration**
   - Good: "add email column"
   - Bad: "add email, fix FK, rename table" (split into 3 migrations)

7. **Document complex migrations**
   ```python
   def upgrade() -> None:
       """
       Add soft delete support to program templates.

       This migration:
       1. Adds is_deleted column (default false)
       2. Creates partial unique index (only for non-deleted)
       3. Adds trigger to prevent assigning deleted programs

       Safe to run with existing data.
       """
       op.add_column(...)
   ```

---

## Troubleshooting

### "Target database is not up to date"
**Cause:** alembic_version has revision that doesn't exist in code
**Fix:** `alembic stamp head` (reset version to match code)

### "Can't locate revision 'abc123'"
**Cause:** Missing migration file
**Fix:** Restore file or stamp to valid revision

### "Multiple heads detected"
**Cause:** Two migrations from same parent (branch in history)
**Fix:** `alembic merge heads -m "merge"` then `upgrade head`

### Migration fails mid-way
**Cause:** SQL error (constraint violation, etc.)
**Result:** Transaction rolled back, no changes applied
**Fix:** Fix the SQL in migration file, then retry

---

## Ready to Test!

You now understand:
- ✅ What each Alembic command does
- ✅ What happens under the hood
- ✅ How to generate, review, apply, and rollback migrations
- ✅ How Alembic tracks schema versions
- ✅ Why migrations are idempotent

**Next:** Follow ALEMBIC-MANUAL-TEST-PLAN.md to run this for real!
