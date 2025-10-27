# Alembic Manual Testing Plan

**Date:** 2025-10-21
**Goal:** Test Alembic configurations manually before running orchestration script
**Time:** ~30-45 minutes

---

## Prerequisites

```bash
# Set DATABASE_URL (from script 01-setup-secrets.sh or Supabase dashboard)
export DATABASE_URL="postgresql://postgres.[PROJECT]:PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

# Verify it's set
echo $DATABASE_URL
```

---

## Phase 1: Test Existing Services (Habits + Movements)

### Test 1: Habits Service (Async Alembic, 2 migrations)

```bash
cd habits_service

# Check current migration status
poetry run alembic current
# Expected: INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
#           (no output = no migrations applied yet)

# Show available migrations
poetry run alembic history
# Expected:
#   189b1231afd4 -> 3b7a1d2e4f56 (head), soft_delete_program_templates
#   <base> -> 189b1231afd4, bootstrap_tables

# Apply migrations
poetry run alembic upgrade head
# Expected:
#   INFO  [alembic.runtime.migration] Running upgrade  -> 189b1231afd4, bootstrap_tables
#   INFO  [alembic.runtime.migration] Running upgrade 189b1231afd4 -> 3b7a1d2e4f56, soft_delete_program_templates

# Verify current status
poetry run alembic current
# Expected: 3b7a1d2e4f56 (head)

# ✅ SUCCESS: Habits service migrations applied
```

**What to check in database:**
```bash
psql "$DATABASE_URL" -c "\dt habits.*"
# Expected tables:
#   habits.alembic_version
#   habits.habits
#   habits.habit_tracking
#   habits.program_templates (or similar)
```

---

### Test 2: Movements Service (Sync Alembic, 1 migration)

```bash
cd ../movements_service

# Check status
poetry run alembic current
# Expected: (no output)

# Show history
poetry run alembic history
# Expected: <base> -> 0001 (head), init

# Apply
poetry run alembic upgrade head
# Expected: INFO  [alembic.runtime.migration] Running upgrade  -> 0001, init

# Verify
poetry run alembic current
# Expected: 0001 (head)

# ✅ SUCCESS: Movements service migrations applied
```

**What to check in database:**
```bash
psql "$DATABASE_URL" -c "\dt movements.*"
# Expected tables:
#   movements.alembic_version
#   movements.exercises (or similar)
#   movements.movements (or similar)
```

---

## Phase 2: Test Idempotency (Run Migrations Twice)

```bash
# Re-run habits (should no-op)
cd ../habits_service
poetry run alembic upgrade head
# Expected: (no output, or "Current revision already at head")

# Re-run movements (should no-op)
cd ../movements_service
poetry run alembic upgrade head
# Expected: (no output, or "Current revision already at head")

# ✅ SUCCESS: Migrations are idempotent
```

---

## Phase 3: Test New Configurations (Practices + Users)

### Test 3: Practices Service (NEW CONFIG)

```bash
cd ../practices_service

# Generate initial migration (auto-detect tables from models)
poetry run alembic revision --autogenerate -m "initial schema"
# Expected:
#   INFO  [alembic.autogenerate.compare] Detected added table 'practices.practices'
#   INFO  [alembic.autogenerate.compare] Detected added table 'practices.prescriptions'
#   ...
#   Generating /path/to/alembic/versions/XXXXX_initial_schema.py ...  done

# IMPORTANT: Review the generated migration file
cat alembic/versions/*_initial_schema.py
# Look for:
#   - op.create_table('practices', ...)
#   - op.create_table('prescriptions', ...)
#   - All expected tables present

# If looks good, apply migration
poetry run alembic upgrade head
# Expected: INFO  [alembic.runtime.migration] Running upgrade  -> XXXXX, initial schema

# Verify
poetry run alembic current
# Expected: XXXXX (head)

# ✅ SUCCESS: Practices service Alembic setup works
```

**What to check in database:**
```bash
psql "$DATABASE_URL" -c "\dt practices.*"
# Expected tables:
#   practices.alembic_version
#   practices.practices (or practice_instances)
#   practices.prescriptions
#   practices.prescribed_movements
#   practices.sets
```

---

### Test 4: Users Service (NEW CONFIG)

```bash
cd ../users_service

# Generate initial migration
poetry run alembic revision --autogenerate -m "initial schema"
# Expected: Generating /path/to/alembic/versions/XXXXX_initial_schema.py ...  done

# Review generated migration
cat alembic/versions/*_initial_schema.py
# Look for:
#   - op.create_table('users.users', ...)
#   - op.create_table('users.user_roles', ...)
#   - All expected tables

# Apply
poetry run alembic upgrade head

# Verify
poetry run alembic current

# ✅ SUCCESS: Users service Alembic setup works
```

**What to check in database:**
```bash
psql "$DATABASE_URL" -c "\dt users.*"
# Expected tables:
#   users.alembic_version
#   users.users
#   users.user_roles (or similar)
```

---

## Phase 4: Test Orchestration Script

```bash
cd ../infra-v2/bootstrap

# Run full orchestration (should apply remaining services + no-op for manual ones)
./03-run-migrations.sh

# Expected output:
# ✅ Running migrations: src/alembic-config
# ✅ Running migrations: habits_service/alembic (NO-OP, already at head)
# ✅ Running migrations: movements_service/alembic (NO-OP, already at head)
# ✅ Running migrations: meals_service/alembic
# ✅ Running migrations: practices_service/alembic (NO-OP, already at head)
# ✅ Running migrations: users_service/alembic (NO-OP, already at head)
# ✅ All Migrations Complete!

# ✅ SUCCESS: Orchestration works with mix of manual + automated
```

---

## Phase 5: Final Verification (All Schemas)

```bash
# Check all schemas have alembic_version table
psql "$DATABASE_URL" -c "
SELECT
    schemaname,
    tablename
FROM pg_tables
WHERE tablename = 'alembic_version'
ORDER BY schemaname;
"

# Expected output:
#  schemaname | tablename
# ------------+----------------
#  habits     | alembic_version
#  journal    | alembic_version  (or public if src/alembic-config uses public)
#  meals      | alembic_version
#  movements  | alembic_version
#  practices  | alembic_version
#  users      | alembic_version

# Check all services have tables
psql "$DATABASE_URL" -c "
SELECT
    schemaname,
    COUNT(*) as table_count
FROM pg_tables
WHERE schemaname IN ('habits', 'journal', 'public', 'meals', 'movements', 'practices', 'users')
GROUP BY schemaname
ORDER BY schemaname;
"

# Expected:
#  schemaname | table_count
# ------------+-------------
#  habits     | 4-5
#  journal    | 3-4 (or public)
#  meals      | 3-4
#  movements  | 3-4
#  practices  | 5-6
#  users      | 3-4

# ✅ SUCCESS: All schemas created with migrations
```

---

## Troubleshooting Common Issues

### Issue 1: "ImportError: cannot import name 'Base'"

**Error:**
```
ImportError: cannot import name 'Base' from 'practices.repository.database'
```

**Solution:**
```bash
# Make sure you're in the service directory
cd practices_service

# Check if models are importable
poetry run python -c "from practices.repository.database import Base; print(Base.metadata.tables.keys())"

# If that works, but Alembic doesn't, check alembic/env.py imports
# Ensure: from practices.repository.database import Base
```

---

### Issue 2: "Target database is not up to date"

**Error:**
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**Solution:**
```bash
# Check what's in database vs code
poetry run alembic current  # Database version
poetry run alembic heads    # Code version

# If different, stamp database with correct version
poetry run alembic stamp head
```

---

### Issue 3: "Can't connect to database"

**Error:**
```
sqlalchemy.exc.OperationalError: could not translate host name "aws-0-us-east-1.pooler.supabase.com" to address
```

**Solution:**
```bash
# Verify DATABASE_URL is set correctly
echo $DATABASE_URL

# Test connection directly
psql "$DATABASE_URL" -c "SELECT 1"

# If psql works but Alembic doesn't, check alembic/env.py DATABASE_URL source
```

---

### Issue 4: "Multiple heads detected"

**Error:**
```
alembic.util.exc.CommandError: Multiple heads are present
```

**Solution:**
```bash
# Show heads
poetry run alembic heads

# Merge heads
poetry run alembic merge -m "merge heads" abc123 def456

# Apply merged migration
poetry run alembic upgrade head
```

---

## Success Criteria Checklist

After completing all phases:

- [ ] Habits service: Migrations applied, no errors
- [ ] Movements service: Migrations applied, no errors
- [ ] Practices service: Initial migration generated and applied
- [ ] Users service: Initial migration generated and applied
- [ ] Src/alembic-config: Migrations applied (via orchestration)
- [ ] Meals service: Migrations applied (via orchestration)
- [ ] Orchestration script runs without errors
- [ ] All services idempotent (can run migrations multiple times)
- [ ] All schemas have alembic_version table
- [ ] All schemas have expected tables
- [ ] No "can't import" or connection errors

---

## Next Steps After Successful Testing

1. ✅ Migrations tested and working
2. ⏭️ Add environment guards to `metadata.create_all()`
3. ⏭️ Update application code for secret volume mounts
4. ⏭️ Build Docker images
5. ⏭️ Run script 04 (RLS policies)
6. ⏭️ Deploy to production

---

## Time Estimate

- Phase 1 (Test habits + movements): 10 mins
- Phase 2 (Test idempotency): 5 mins
- Phase 3 (Test practices + users): 15 mins
- Phase 4 (Test orchestration): 5 mins
- Phase 5 (Verification): 5 mins
- **Total: 40 minutes**

---

## Notes for You

- Take your time reviewing generated migrations (cat the .py files)
- If a migration looks wrong, delete it and regenerate: `rm alembic/versions/XXXXX_*.py`
- Save the DATABASE_URL in your shell profile if you'll be testing multiple times
- The orchestration script is smart - it skips services already at head

**You got this!** The configs are set up correctly, just need to generate initial migrations for practices + users.
