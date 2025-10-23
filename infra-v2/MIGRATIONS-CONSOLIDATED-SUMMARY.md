# Migration Consolidation - Complete Summary

**Date:** 2025-10-22
**Status:** ✅ ALL MIGRATIONS CONSOLIDATED & READY FOR TESTING
**Next Step:** Manual testing using ALEMBIC-MANUAL-TEST-PLAN-UPDATED.md

---

## What We Did

Consolidated all existing migrations into **single base migrations** for first production deployment. This is the right approach because:

1. **First production deployment** - no historical baggage
2. **Clean slate** - start with complete schema in one migration
3. **Easier to understand** - one file per service shows entire schema
4. **Faster to apply** - single migration vs multiple sequential ones

---

## Migration Files Created/Updated

### ✅ habits_service
**Before:** 3 migrations (189b1231afd4, 2a3f4c9d1cde, 3b7a1d2e4f56)
**After:** 1 migration (`001_initial_schema.py`)

**Includes:**
- All 16 tables (habit_templates, lesson_templates, program_templates, etc.)
- CASCADE delete behaviors for program hierarchies
- Soft delete functionality (is_deleted column + triggers)
- All indexes, constraints, and foreign keys

**Location:** `habits_service/alembic/versions/001_initial_schema.py`

---

### ✅ meals_service
**Before:** 2 migrations (0001_init, 0002_off_fields)
**After:** 1 migration (`001_initial_schema.py`)

**Includes:**
- All 5 tables (food_items, user_goals, meals, meal_foods, water_consumption)
- Open Food Facts integration fields (brand, external_id, etc.)
- meal_type enum
- All indexes

**Location:** `meals_service/alembic/versions/001_initial_schema.py`

---

### ✅ practices_service (NEW)
**Before:** No migrations
**After:** 1 migration (`001_initial_schema.py`)

**Includes:**
- 19 tables total:
  - Template tables: practice_templates, prescription_templates, movement_templates, set_templates
  - Instance tables: practice_instances, prescription_instances, movement_instances, set_instances
  - Program tables: programs, program_tags, program_practice_links
  - Enrollment: program_enrollments, scheduled_practices
- enrollment_status_enum
- All check constraints, foreign keys, indexes

**Location:** `practices_service/alembic/versions/001_initial_schema.py`

---

### ✅ users_service (NEW)
**Before:** No migrations
**After:** 1 migration (`001_initial_schema.py`)

**Includes:**
- 7 tables:
  - users (supabase_id, keycloak_id, email, first_name, last_name)
  - services (meals, practice, sleep, etc.)
  - user_services (linking table)
  - schedulables (federated tasks)
  - user_roles (role-domain assignments)
  - coach_client_relationships (simplified)
  - coach_client_associations (domain-specific)
- 4 enums: service_type, role_enum, domain_enum, association_status_enum
- All indexes and constraints

**Location:** `users_service/alembic/versions/001_initial_schema.py`

---

### ✅ movements_service (UNCHANGED)
**Status:** Already had 1 migration
**File:** `movements_service/alembic/versions/0001_init.py`

No changes needed - already consolidated.

---

### ✅ agent + journal (UNCHANGED)
**Status:** Already had 1 migration
**File:** `src/alembic-config/alembic/versions/3e41ce1dbfee_m.py`

No changes needed - already consolidated.

---

## How to Test

Follow the updated manual test plan:

```bash
# Read the test plan
cat /home/peleke/Documents/Projects/swae/MindMirror/infra-v2/ALEMBIC-MANUAL-TEST-PLAN-UPDATED.md

# Or start testing immediately:
cd /home/peleke/Documents/Projects/swae/MindMirror

# Test habits service
cd habits_service
export DATABASE_URL="postgresql://..."
poetry run alembic current
poetry run alembic history
poetry run alembic upgrade head
poetry run alembic current

# Test practices service
cd ../practices_service
poetry run alembic upgrade head

# Test users service
cd ../users_service
poetry run alembic upgrade head

# Verify in database
psql "$DATABASE_URL" -c "SELECT schemaname, COUNT(*) FROM pg_tables WHERE schemaname IN ('habits', 'practices', 'users') GROUP BY schemaname;"
```

---

## Key Commands for Each Service

### Habits Service
```bash
cd habits_service
poetry run alembic upgrade head  # Apply migration
poetry run alembic current       # Check status (should show: 001 (head))
```

### Practices Service
```bash
cd practices_service
poetry run alembic upgrade head  # Apply migration
poetry run alembic current       # Check status (should show: 001 (head))
```

### Users Service
```bash
cd users_service
poetry run alembic upgrade head  # Apply migration
poetry run alembic current       # Check status (should show: 001 (head))
```

### Meals Service
```bash
cd meals_service
poetry run alembic upgrade head  # Apply migration
poetry run alembic current       # Check status (should show: 001 (head))
```

### Movements Service
```bash
cd movements_service
poetry run alembic upgrade head  # Apply migration
poetry run alembic current       # Check status (should show: 0001 (head))
```

---

## Documentation Files

### Primary Documents (Use These)
1. **ALEMBIC-MANUAL-TEST-PLAN-UPDATED.md** ← Start here for testing
2. **MIGRATIONS-CONSOLIDATED-SUMMARY.md** ← This file (overview)
3. **ALEMBIC-SETUP-GUIDE.md** ← Quick command reference

### Legacy Documents (For Context)
- **ALEMBIC-MANUAL-TEST-PLAN.md** - Old plan (before consolidation)
- **ALEMBIC-WALKTHROUGH.md** - Detailed walkthrough of habits_service
- **HABITS-SERVICE-ALEMBIC-FORENSICS.md** - Forensic analysis that found the gaps
- **READY-FOR-MIGRATIONS.md** - Old summary
- **SESSION-SUMMARY-ALEMBIC.md** - Previous session notes

---

## Expected Results

After running all migrations, you should have:

### Database Schemas
- ✅ `habits` - 16 tables
- ✅ `practices` - 19 tables
- ✅ `users` - 7 tables
- ✅ `meals` - 5 tables
- ✅ `movements` - 3-4 tables

### Alembic Version Tables
```sql
-- Check all services have version tracking
SELECT schemaname, tablename
FROM pg_tables
WHERE tablename = 'alembic_version'
ORDER BY schemaname;

-- Expected:
--  schemaname | tablename
-- ------------+----------------
--  habits     | alembic_version
--  meals      | alembic_version
--  movements  | alembic_version
--  practices  | alembic_version
--  users      | alembic_version
```

---

## Next Steps After Testing

1. ✅ Test migrations manually (~20-30 mins)
2. ⏭️ Add environment guards to `metadata.create_all()` calls
3. ⏭️ Update migration orchestration script (if needed)
4. ⏭️ Update application code for secret volume mounts
5. ⏭️ Build and push Docker images
6. ⏭️ Run remaining bootstrap scripts
7. ⏭️ Deploy to production

---

## Why This Approach is Better

### Old Approach (Historical Migrations)
- 3 migrations for habits_service (189b... → 2a3f... → 3b7a...)
- 2 migrations for meals_service (0001 → 0002)
- Complex to understand and debug
- Slower to apply (sequential execution)

### New Approach (Consolidated)
- **1 migration per service**
- Complete schema visible in one file
- Faster to apply (single transaction)
- **Perfect for first production deployment**
- Adopt incremental workflow from here forward

---

## Migration Workflow Going Forward

After this initial deployment:

1. **Make model changes** in SQLAlchemy models
2. **Generate migration:**
   ```bash
   cd service_name
   poetry run alembic revision --autogenerate -m "add email column"
   ```
3. **Review generated migration** (always check the file!)
4. **Apply migration:**
   ```bash
   poetry run alembic upgrade head
   ```
5. **Commit migration file** to git

This gives you full migration history moving forward while starting clean.

---

## Summary

✅ **All migrations consolidated**
✅ **Ready for first production deployment**
✅ **Clean slate with full feature parity**
✅ **Migration workflow in place for future changes**

**Next:** Run the manual test plan and verify everything works! 🚀
