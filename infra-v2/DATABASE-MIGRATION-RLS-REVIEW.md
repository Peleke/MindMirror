# Database Migration & RLS Strategy Review

**Status:** ⚠️ CRITICAL ISSUES FOUND - MUST FIX BEFORE PRODUCTION
**Date:** 2025-10-21
**Reviewer:** DevOps (Alex)

---

## TL;DR: What Needs to Happen

Before running scripts 03 (migrations) and 04 (RLS):

1. ❌ **Create Alembic configs** for practices_service and users_service
2. ❌ **Remove `metadata.create_all()` from production code** (4+ services affected)
3. ✅ **Verify RLS doesn't conflict with service-level auth** (appears safe, but needs testing)
4. ⚠️ **Generate initial Alembic migrations** for all services
5. ⚠️ **Test migration path** in staging before production

**Estimated effort:** 2-3 hours
**Risk if skipped:** Schema drift, production schema conflicts, data loss

---

## Issue 1: Missing Alembic Configurations

### Current State

**✅ Services WITH Alembic:**
```
src/alembic-config/         → Agent + Journal services (main DB, public schema)
habits_service/alembic/     → Habits service (habits schema)
meals_service/alembic/      → Meals service (meals schema)
movements_service/alembic/  → Movements service (movements schema)
```

**❌ Services MISSING Alembic:**
```
practices_service/          → ❌ NO alembic/ directory
users_service/              → ❌ NO alembic/ directory
```

### Why This Is a Problem

Without Alembic:
- No versioned schema history
- Can't track what schema changes were applied
- Can't roll back schema changes
- Can't reproduce production schema in new environments
- **Will conflict with metadata.create_all() during deployment**

### What To Do

#### Option A: Create Alembic Configs NOW (Recommended)
```bash
# For practices_service
cd practices_service
poetry run alembic init alembic

# Edit alembic.ini:
# - Set sqlalchemy.url = postgresql+asyncpg://...
# - Set script_location = alembic

# Edit alembic/env.py:
# - Import practices.repository.models.Base
# - Set target_metadata = Base.metadata
# - Configure schema = "practices"

# Generate initial migration
poetry run alembic revision --autogenerate -m "initial schema"

# Review migration file (will be in alembic/versions/)
# Ensure it captures all tables, indexes, constraints

# For users_service (repeat process)
cd users_service
poetry run alembic init alembic
# ... same steps ...
```

#### Option B: Skip Alembic, Use metadata.create_all() (NOT Recommended)
- Keep calling `Base.metadata.create_all()` in services
- Accept schema drift risk
- No migration history
- Hard to debug production issues
- **NOT ACCEPTABLE FOR PRODUCTION**

### Recommendation

✅ **Option A** - Create Alembic configs for practices_service and users_service **before** running script 03.

**Timeline:**
- practices_service Alembic setup: 30 mins
- users_service Alembic setup: 30 mins
- Generate + review migrations: 30 mins
- **Total: 1.5 hours**

---

## Issue 2: metadata.create_all() in Production Code

### Current State

**Services calling `Base.metadata.create_all()` on startup:**

#### 1. practices_service/practices/repository/database.py:44
```python
async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    # ...
    async with engine.begin() as conn:
        await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "practices"'))
        await conn.run_sync(Base.metadata.create_all)  # ← PROBLEM
```

#### 2. users_service/users/repository/database.py:83
```python
async def init_db() -> None:
    """Initialize the database, ensure schema exists, and create tables if they don't exist."""
    async with engine.connect() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))
        await conn.commit()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ← PROBLEM
```

#### 3. meals_service/meals/repository/database.py:46
```python
async def init_db() -> None:
    """Initialize the database, creating tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS meals"))
        await conn.run_sync(Base.metadata.create_all)  # ← PROBLEM
```

#### 4. habits_service (likely, need to verify)
Probably also has this pattern.

### Why This Is a Problem

**Schema Management Conflict:**
- Alembic manages schema via versioned migrations
- `create_all()` creates schema directly from Python models
- **Both are trying to manage the same schema!**

**Production Deployment Issues:**
```python
# Scenario 1: First deployment
# - Alembic migration runs: Creates tables v1
# - Service starts: Calls create_all(), sees tables exist, does nothing
# Result: ✅ Works (by accident)

# Scenario 2: Schema change deployment
# - Developer updates model (adds column)
# - Alembic migration runs: Adds column
# - Service starts: Calls create_all(), sees table structure different
# Result: ❌ SQLAlchemy might try to ALTER table, or silently fail

# Scenario 3: Service restart after Alembic rollback
# - Alembic rolls back migration (removes column)
# - Service starts: Calls create_all() with NEW model
# - create_all() re-adds column that was just removed
# Result: ❌ Rollback UNDONE by service startup!

# Scenario 4: Multiple service instances
# - Service A starts: Calls create_all(), begins creating tables
# - Service B starts: Calls create_all(), tries to create same tables
# Result: ⚠️ Race condition, possible deadlocks
```

### What To Do

**Step 1: Make `create_all()` environment-aware**

Add environment variable to control schema creation:

```python
# practices_service/practices/repository/database.py
import os

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    # Only create schema automatically in development
    if os.getenv("ENVIRONMENT", "development") == "development":
        async with engine.begin() as conn:
            await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "practices"'))
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created (if they didn't exist).")
    else:
        # Production: Rely on Alembic migrations
        print("Production mode: Skipping auto-create. Use Alembic migrations.")
```

**Step 2: Update ALL services** (practices, users, meals, habits)

Same pattern for each:
```python
if os.getenv("ENVIRONMENT", "development") == "development":
    await conn.run_sync(Base.metadata.create_all)
else:
    # Production: Schema managed by Alembic
    pass
```

**Step 3: Update infra-v2 to set ENVIRONMENT=production**

Already done! Check modules:
```hcl
# infra-v2/modules/practices_service/main.tf
env_vars = [
  {
    name  = "ENVIRONMENT"
    value = var.environment  # Will be "production"
  },
  # ...
]
```

### Recommendation

✅ **Add environment guards** to ALL `init_db()` functions **before** production deployment.

**Timeline:**
- Update practices_service: 10 mins
- Update users_service: 10 mins
- Update meals_service: 10 mins
- Update habits_service: 10 mins
- Test in local dev: 20 mins
- **Total: 1 hour**

---

## Issue 3: RLS vs Service-Level RBAC Conflict

### Current Architecture

**Two layers of authorization:**

#### Layer 1: Application-Level (Services)
- Services use `SERVICE_ROLE` Supabase key (from Secret Manager)
- `get_current_user()` extracts `x-internal-id` header
- Fetches user roles from users_service
- Python code checks roles: `current_user.has_role("admin", "practices")`
- **Location:** src/shared/auth.py, services' resolvers

#### Layer 2: Database-Level (RLS Policies)
- RLS policies check `auth.uid()` (from Supabase JWT)
- Applied to tables: vouchers, journal_entries, habits, practice_instances, meals, movements
- Users can only access rows where `user_id = auth.uid()`
- **Location:** infra-v2/bootstrap/04-apply-rls-policies.sh

### How They Interact

**Normal Request Flow:**
```
1. Client sends request with JWT (Authorization: Bearer <token>)
2. Gateway forwards to service with x-internal-id header
3. Service connects to DB with SERVICE_ROLE key
4. Service queries: SELECT * FROM practices.practice_instances WHERE user_id = :internal_id
5. RLS policy: Checks auth.uid() from JWT
   - BUT: Service uses SERVICE_ROLE → RLS is BYPASSED
6. Service-level auth: Python code checks current_user.has_role(...)
7. Response returned to client
```

**Key Insight:**
```sql
-- When service uses SERVICE_ROLE:
SET ROLE service_role;  -- RLS policies are BYPASSED

-- The policy says:
CREATE POLICY "Users can view own practices"
  ON practice_instances
  FOR SELECT
  USING (auth.uid()::text = user_id);

-- But auth.uid() is NULL when using SERVICE_ROLE
-- So the USING clause is skipped entirely!
```

### Is This a Problem?

**NO - This is BY DESIGN:**

✅ **Services are TRUSTED** to enforce authorization in application code
✅ **RLS policies protect against:**
   - Direct Supabase client access (if client SDK is used)
   - Leaked database credentials
   - SQL injection attacks
   - Bypass of service layer

❌ **RLS policies DO NOT protect against:**
   - Bugs in service authorization logic
   - Service-level authorization bypass
   - Services querying wrong data (e.g., missing WHERE user_id = :id)

### Potential Issues

#### Issue 3.1: Service Forgets to Filter by user_id

**Bad code:**
```python
# practices_service/practices/service/services/practice_service.py
async def get_all_practices(self, session: AsyncSession):
    # WRONG: No user_id filter!
    result = await session.execute(
        select(PracticeInstanceModel)
    )
    return result.scalars().all()  # Returns ALL users' practices!
```

**What happens:**
- Service uses SERVICE_ROLE → RLS bypassed
- Query returns ALL practices from ALL users
- Resolver returns data to wrong user
- **Security breach!**

**RLS does NOT save you** because service uses SERVICE_ROLE.

**Fix:**
```python
async def get_all_practices(self, session: AsyncSession, user_id: UUID):
    # CORRECT: Filter by user_id
    result = await session.execute(
        select(PracticeInstanceModel).where(PracticeInstanceModel.user_id == user_id)
    )
    return result.scalars().all()
```

#### Issue 3.2: Service Queries with Wrong User Context

**Bad code:**
```python
# practices_service/resolvers.py
@strawberry.type
class Query:
    @strawberry.field
    async def get_practice(self, practice_id: UUID) -> Practice:
        # WRONG: No user context check!
        session = get_session()
        practice = await session.get(PracticeInstanceModel, practice_id)
        return practice  # Might belong to different user!
```

**What happens:**
- User A requests User B's practice_id
- Service queries DB with SERVICE_ROLE
- RLS bypassed → query succeeds
- User A sees User B's data
- **Security breach!**

**Fix:**
```python
@strawberry.field
async def get_practice(
    self,
    practice_id: UUID,
    info: Info
) -> Practice:
    current_user = info.context["current_user"]  # From get_current_user()
    session = get_session()

    practice = await session.get(PracticeInstanceModel, practice_id)

    # CRITICAL: Verify ownership
    if practice.user_id != current_user.id:
        raise PermissionError("Not authorized to access this practice")

    return practice
```

### Does Our Code Have These Issues?

**Need to audit:**
- [ ] practices_service/practices/web/graphql/resolvers.py
- [ ] users_service/users/web/graphql/resolvers.py
- [ ] meals_service (if has GraphQL resolvers)
- [ ] movements_service (if has GraphQL resolvers)
- [ ] habits_service (if has GraphQL resolvers)

**Look for:**
- Queries without `user_id` filter
- Resolvers that don't check `current_user.id` before returning data
- Mutations that allow modifying other users' data

### Recommendation

✅ **RLS policies are SAFE to apply** - they provide defense in depth
⚠️ **BUT: Must audit service code for proper authorization checks**

**Timeline:**
- Audit practices_service resolvers: 30 mins
- Audit users_service resolvers: 30 mins
- Audit other services: 30 mins
- Fix any issues found: 1-2 hours
- **Total: 2-3 hours**

---

## Issue 4: Incomplete Alembic Migrations

### Current State

**src/alembic-config/alembic/versions/** (Agent + Journal services):
```
Only 1 migration file: 3e41ce1dbfee_m.py
```

This seems suspicious. The agent and journal services have multiple tables (journal_entries, vouchers, etc.) but only 1 migration?

**habits_service/alembic/versions/**:
```
- 189b1231afd4_bootstrap_tables.py
- 3b7a1d2e4f56_soft_delete_program_templates.py
```
✅ This looks better - initial schema + 1 change.

**meals_service/alembic/versions/**:
```
- 0001_init.py
- 0002_off_fields.py
```
✅ Looks good.

**movements_service/alembic/versions/**:
```
- 0001_init.py
```
✅ Initial migration present.

### What To Do

#### Check if src/alembic-config migration is complete:

```bash
# Generate a new migration to see what's missing
cd src/alembic-config
poetry run alembic revision --autogenerate -m "check_missing_tables"

# If output shows new tables/columns, then initial migration was incomplete
# If output is empty, then current migration is complete
```

#### If incomplete, consolidate or create new migration:

**Option A: Squash into single migration (if DB is empty)**
```bash
# Drop existing migration
rm alembic/versions/3e41ce1dbfee_m.py

# Generate fresh complete migration
poetry run alembic revision --autogenerate -m "initial_schema"
```

**Option B: Create additional migration (if DB has data)**
```bash
# Keep existing migration
# Create new migration for missing pieces
poetry run alembic revision --autogenerate -m "add_missing_tables"
```

### Recommendation

✅ **Verify src/alembic-config completeness** before running script 03.

**Timeline:** 15 mins to check, 30 mins to fix if needed

---

## Complete Action Plan

### Before Running Script 03 (Migrations)

**Priority 1: Critical** (MUST DO)
1. [ ] Create Alembic config for practices_service (30 mins)
2. [ ] Create Alembic config for users_service (30 mins)
3. [ ] Generate initial migrations for practices + users (30 mins)
4. [ ] Verify src/alembic-config migration completeness (15 mins)
5. [ ] Add environment guards to `metadata.create_all()` in all services (1 hour)

**Priority 2: Important** (SHOULD DO)
6. [ ] Review Alembic env.py configs for all services (30 mins)
7. [ ] Test migration path in local Docker (30 mins)
8. [ ] Create rollback plan for each service (30 mins)

**Priority 3: Validation** (NICE TO HAVE)
9. [ ] Dry-run all migrations with `--sql` flag (15 mins)
10. [ ] Document migration dependency order (15 mins)

**Total Time:** 4-5 hours

---

### Before Running Script 04 (RLS)

**Priority 1: Critical** (MUST DO)
1. [ ] Audit practices_service for authorization checks (30 mins)
2. [ ] Audit users_service for authorization checks (30 mins)
3. [ ] Audit other services with GraphQL resolvers (1 hour)

**Priority 2: Important** (SHOULD DO)
4. [ ] Fix any authorization bypass issues found (1-2 hours)
5. [ ] Add integration tests for RLS + service auth (1 hour)
6. [ ] Document service auth vs RLS relationship (30 mins)

**Total Time:** 3-4 hours

---

## Script Execution Order (Updated)

### Current Plan (WRONG):
```bash
./01-setup-secrets.sh      # ✅ Done
./02-setup-supabase.sh     # ⏭️ Skipped (manual)
./03-run-migrations.sh     # ❌ DON'T RUN YET
./04-apply-rls-policies.sh # ❌ DON'T RUN YET
```

### Corrected Plan (RIGHT):
```bash
# 1. Prerequisites (2-3 hours)
cd practices_service
alembic init alembic
# ... configure alembic.ini, env.py ...
alembic revision --autogenerate -m "initial schema"

cd ../users_service
# ... repeat ...

# Update all init_db() functions with environment guards

# 2. Test locally (30 mins)
docker-compose down -v
docker-compose up -d postgres
cd src/alembic-config && alembic upgrade head
cd habits_service && alembic upgrade head
# ... etc for all services ...

# 3. THEN run production scripts
cd infra-v2/bootstrap
./03-run-migrations.sh     # ✅ NOW safe to run

# 4. Audit authorization (3-4 hours)
# ... review resolvers ...
# ... fix issues ...

# 5. Apply RLS
./04-apply-rls-policies.sh # ✅ NOW safe to run
```

---

## Risk Assessment

### If You Skip This Work:

**Scenario 1: Run script 03 without Alembic configs**
```bash
./03-run-migrations.sh
# Runs migrations for: agent, journal, habits, meals, movements
# SKIPS: practices, users (no Alembic configs)
# Result: ⚠️ Partial schema created
#         ❌ practices_service calls create_all() on startup
#         ❌ users_service calls create_all() on startup
#         ⚠️ Schema drift starts immediately
```

**Scenario 2: Run script 04 without authorization audit**
```bash
./04-apply-rls-policies.sh
# Applies RLS policies
# Result: ✅ RLS protects against direct DB access
#         ❌ Services use SERVICE_ROLE (RLS bypassed)
#         ❌ Authorization bugs in resolvers still exist
#         ⚠️ False sense of security
```

**Scenario 3: Deploy with create_all() in production**
```bash
tofu apply
# Services start with ENVIRONMENT=production
# practices_service: Calls create_all()
# users_service: Calls create_all()
# Result: ⚠️ Alembic migration ran, then create_all() ran
#         ⚠️ Schema might diverge from migration history
#         ❌ Future rollbacks will fail
```

---

## Recommended Timeline

### Option A: Do It Right (Recommended)
```
Day 1 (Today):
- Hour 1-2: Create Alembic configs (practices, users)
- Hour 2-3: Generate + review initial migrations
- Hour 3-4: Add environment guards to init_db()
- Hour 4-5: Test migration path locally

Day 2 (Tomorrow):
- Hour 1-3: Audit service authorization
- Hour 3-4: Fix any issues found
- Hour 4-5: Run scripts 03 + 04 in production

Total: 2 days, ~10 hours
```

### Option B: Quick & Dirty (NOT Recommended)
```
Today:
- Skip Alembic for practices/users (use create_all())
- Skip authorization audit (trust existing code)
- Run scripts 03 + 04
- Hope for the best

Result: ⚠️ Production works initially
        ❌ Schema drift over time
        ❌ Authorization bugs might exist
        ❌ Hard to debug later
        ❌ Can't roll back schema changes

Total: 2 hours, high risk
```

---

## My Recommendation

**DO OPTION A.**

Yes, it's 10 more hours of work. But you said it yourself:

> "this is super high risk stuff, you know we got to get it right"
> "we still can't be making mistakes at this level"
> "this is supposed to be our production environment"

**The risk of skipping this work:**
- Schema conflicts on deployment
- Authorization bypass vulnerabilities
- Can't roll back bad migrations
- Production debugging nightmare

**The benefit of doing this work:**
- Clean, versioned schema history
- Confidence in authorization layer
- Can roll back any deployment
- Production environment you can trust

Take the extra day. Get it right. Sleep well at night.

---

## Questions?

- Need help setting up Alembic configs?
- Want me to audit the resolver authorization?
- Need a test plan for migration path?
- Want to discuss RLS vs service auth more?

Let me know and I'll dive deeper into any of these areas.
