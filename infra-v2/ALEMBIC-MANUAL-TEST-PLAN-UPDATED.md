# Alembic Manual Testing Plan (UPDATED for Consolidated Migrations)

**Date:** 2025-10-22
**Status:** Ready for testing with consolidated base migrations
**Goal:** Test consolidated Alembic migrations before production deployment
**Time:** ~20-30 minutes

---

## What Changed

We've **consolidated all migrations into single base migrations** for first production deployment:

- **habits_service:** 3 migrations → 1 consolidated (`001_initial_schema.py`)
- **meals_service:** 2 migrations → 1 consolidated (`001_initial_schema.py`)
- **practices_service:** NEW - `001_initial_schema.py` (19 tables)
- **users_service:** NEW - `001_initial_schema.py` (7 tables)
- **movements_service:** Already 1 migration (`0001_init.py`) ✅
- **agent + journal:** Already 1 migration (`3e41ce1dbfee_m.py`) ✅

**Why?** Since this is the **first production deployment**, we don't need historical migrations. We start with a clean slate and adopt migration workflow moving forward.

---

## Prerequisites

```bash
# Set DATABASE_URL (from Supabase or local database)
export DATABASE_URL="postgresql://postgres.[PROJECT]:PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# Verify it's set
echo $DATABASE_URL
```

---

## Phase 1: Test Core Services

### Test 1: Habits Service (16 tables - comprehensive test)

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/habits_service

# Check current migration status (should be empty)
poetry run alembic current
# Expected: (no output = no migrations applied yet)

# Show available migrations
poetry run alembic history
# Expected: <base> -> 001 (head), initial schema - complete habits service database

# Apply migration
poetry run alembic upgrade head
# Expected:
#   INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial schema
#   Creates habits schema
#   Creates all 16 tables with CASCADE behaviors, soft delete, triggers

# Verify current status
poetry run alembic current
# Expected: 001 (head)

# ✅ SUCCESS: Habits service migration applied
```

**What to check in database:**
```bash
psql "$DATABASE_URL" -c "\dt habits.*"
# Expected tables:
#   habits.alembic_version
#   habits.habit_templates
#   habits.lesson_templates
#   habits.program_templates (with is_deleted column)
#   habits.program_step_templates
#   habits.step_lesson_templates
#   habits.lesson_segments
#   habits.step_daily_plan
#   habits.user_program_assignments
#   habits.habit_events
#   habits.lesson_events
#   habits.journal_task_events
#   habits.lesson_tasks
#   habits.template_access
#   habits.template_provenance
```

---

### Test 2: Practices Service (19 tables - NEW)

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/practices_service

# Check status
poetry run alembic current
# Expected: (no output)

# Show history
poetry run alembic history
# Expected: <base> -> 001 (head), initial schema - complete practices service database

# Apply
poetry run alembic upgrade head
# Expected: INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial schema

# Verify
poetry run alembic current
# Expected: 001 (head)

# ✅ SUCCESS: Practices service migration applied
```

**What to check in database:**
```bash
psql "$DATABASE_URL" -c "\dt practices.*"
# Expected tables (19 total):
#   practices.alembic_version
#   practices.practice_templates
#   practices.prescription_templates
#   practices.movement_templates
#   practices.set_templates
#   practices.practice_instances
#   practices.prescription_instances
#   practices.movement_instances
#   practices.set_instances
#   practices.programs
#   practices.program_tags
#   practices.program_practice_links
#   practices.program_enrollments
#   practices.scheduled_practices
```

---

### Test 3: Users Service (7 tables - NEW)

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/users_service

# Check status
poetry run alembic current
# Expected: (no output)

# Show history
poetry run alembic history
# Expected: <base> -> 001 (head), initial schema - complete users service database

# Apply
poetry run alembic upgrade head
# Expected: INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial schema

# Verify
poetry run alembic current
# Expected: 001 (head)

# ✅ SUCCESS: Users service migration applied
```

**What to check in database:**
```bash
psql "$DATABASE_URL" -c "\dt users.*"
# Expected tables:
#   users.alembic_version
#   users.users (supabase_id, keycloak_id, email)
#   users.services
#   users.user_services
#   users.schedulables
#   users.user_roles
#   users.coach_client_relationships
#   users.coach_client_associations
```

---

## Phase 2: Test Idempotency (Run Migrations Twice)

```bash
# Re-run habits (should no-op)
cd /home/peleke/Documents/Projects/swae/MindMirror/habits_service
poetry run alembic upgrade head
# Expected: INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
#          (no "Running upgrade" message = already at head)

# Re-run practices (should no-op)
cd /home/peleke/Documents/Projects/swae/MindMirror/practices_service
poetry run alembic upgrade head
# Expected: (no upgrade output)

# Re-run users (should no-op)
cd /home/peleke/Documents/Projects/swae/MindMirror/users_service
poetry run alembic upgrade head
# Expected: (no upgrade output)

# ✅ SUCCESS: Migrations are idempotent
```

---

## Phase 3: Test Remaining Services

### Test 4: Meals Service (5 tables - consolidated)

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/meals_service

poetry run alembic current
# Expected: (no output)

poetry run alembic upgrade head
# Expected: Running upgrade  -> 001, initial schema

poetry run alembic current
# Expected: 001 (head)

# ✅ SUCCESS: Meals service migration applied
```

---

### Test 5: Movements Service (already has 1 migration)

```bash
cd /home/peleke/Documents/Projects/swae/MindMirror/movements_service

poetry run alembic upgrade head
# Expected: Running upgrade  -> 0001, init

poetry run alembic current
# Expected: 0001 (head)

# ✅ SUCCESS: Movements service migration applied
```

---

## Phase 4: Final Verification (All Schemas)

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
#  meals      | alembic_version
#  movements  | alembic_version
#  practices  | alembic_version
#  users      | alembic_version

# Check table counts
psql "$DATABASE_URL" -c "
SELECT
    schemaname,
    COUNT(*) as table_count
FROM pg_tables
WHERE schemaname IN ('habits', 'meals', 'movements', 'practices', 'users')
GROUP BY schemaname
ORDER BY schemaname;
"

# Expected:
#  schemaname | table_count
# ------------+-------------
#  habits     | 16-17 (16 + alembic_version)
#  meals      | 6 (5 + alembic_version)
#  movements  | 3-4
#  practices  | 20 (19 + alembic_version)
#  users      | 8 (7 + alembic_version)

# ✅ SUCCESS: All schemas created with migrations
```

---

## Troubleshooting Common Issues

### Issue 1: "Can't locate revision identified by '001'"

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by '001'
```

**Cause:** You're in the wrong directory or migration file doesn't exist

**Solution:**
```bash
# Check you're in the right service directory
pwd
# Should be: /path/to/habits_service (or practices_service, etc.)

# Check migration file exists
ls alembic/versions/
# Should see: 001_initial_schema.py

# If not there, you may need to navigate up:
cd ..
cd habits_service
```

---

### Issue 2: "Target database is not up to date"

**Error:**
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**Cause:** Database has old migrations from before consolidation

**Solution:**
```bash
# Clear old migrations
psql "$DATABASE_URL" -c "DELETE FROM habits.alembic_version;"

# Re-run migration
poetry run alembic upgrade head
```

---

### Issue 3: "Table already exists"

**Error:**
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable) relation "habits.habit_templates" already exists
```

**Cause:** Tables were created by `metadata.create_all()` before migrations

**Solution:**
```bash
# Option A: Drop the schema and start fresh
psql "$DATABASE_URL" -c "DROP SCHEMA IF EXISTS habits CASCADE;"
poetry run alembic upgrade head

# Option B: Stamp database as migrated (if tables match migration)
poetry run alembic stamp head
```

---

## Success Criteria Checklist

After completing all phases:

- [ ] Habits service: Migration `001` applied, 16 tables created
- [ ] Practices service: Migration `001` applied, 19 tables created
- [ ] Users service: Migration `001` applied, 7 tables created
- [ ] Meals service: Migration `001` applied, 5 tables created
- [ ] Movements service: Migration `0001` applied
- [ ] All services idempotent (can run migrations multiple times)
- [ ] All schemas have alembic_version table
- [ ] All schemas have expected table counts
- [ ] No "can't import" or connection errors

---

## Next Steps After Successful Testing

1. ✅ Migrations tested and working
2. ⏭️ Add environment guards to `metadata.create_all()`
3. ⏭️ Update migration orchestration script (if needed)
4. ⏭️ Update application code for secret volume mounts
5. ⏭️ Build Docker images
6. ⏭️ Run script 04 (RLS policies)
7. ⏭️ Deploy to production

---

## Time Estimate

- Phase 1 (Test 3 core services): 10 mins
- Phase 2 (Test idempotency): 3 mins
- Phase 3 (Test remaining services): 5 mins
- Phase 4 (Verification): 5 mins
- **Total: 23 minutes**

---

## Notes

- **No need to generate migrations** - we've already created consolidated base migrations
- All migrations are named `001_initial_schema.py` (except movements: `0001_init.py`)
- These are **complete, production-ready** migrations with all features included
- Safe to run multiple times (idempotent)
- Start fresh - perfect for first production deployment

**You got this!** 🚀
