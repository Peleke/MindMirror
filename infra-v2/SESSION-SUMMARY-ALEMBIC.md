# Session Summary: Alembic Setup & Production Deployment Prep

**Date:** 2025-10-21
**Status:** Ready for Option A implementation (missing base migration fix)
**Token Usage:** ~97% (compaction needed)

---

## What We Accomplished

### 1. ✅ Reviewed & Fixed Existing Alembic Configs
- **src/alembic-config/** - Complex but functional (Agent + Journal)
- **habits_service/alembic/** - ⚠️ **BROKEN** (missing base migration)
- **meals_service/alembic/** - Fixed deprecated `AsyncEngine` API
- **movements_service/alembic/** - Clean sync setup

### 2. ✅ Created New Alembic Configs
- **practices_service/alembic/** - Complete setup (async, based on habits pattern)
- **users_service/alembic/** - Complete setup (async, based on habits pattern)

### 3. ✅ Created Comprehensive Documentation
- **ALEMBIC-SETUP-GUIDE.md** - Command reference, patterns, troubleshooting
- **ALEMBIC-MANUAL-TEST-PLAN.md** - Step-by-step testing workflow (40 mins)
- **ALEMBIC-WALKTHROUGH.md** - Complete end-to-end Alembic explanation
- **HABITS-SERVICE-ALEMBIC-FORENSICS.md** - Forensic analysis of broken migrations
- **READY-FOR-MIGRATIONS.md** - High-level summary and action items
- **DATABASE-MIGRATION-RLS-REVIEW.md** - Migration + RLS strategy analysis
- **PHASE-2-RISK-ANALYSIS.md** - VPC/auth hardening deferral strategy

---

## Critical Issue Found: habits_service Missing Base Migration

### The Problem
```
Expected chain:
<base> → '189b1231afd4' → '2a3f4c9d1cde' → '3b7a1d2e4f56'
         ^^^^^^^^^^^^^^
         MISSING FILE!

Actual files:
- 189b1231afd4_bootstrap_tables.py (contains revision '2a3f4c9d1cde') ← MISMATCH!
- 3b7a1d2e4f56_soft_delete_program_templates.py (contains '3b7a1d2e4f56')

Result:
❌ alembic upgrade head → ERROR: "Can't locate revision '189b1231afd4'"
❌ Fresh database deployment will FAIL
⚠️ Works in dev because tables created with metadata.create_all()
```

### Why It Happened
September 17, 2025 - Someone accidentally overwrote the base migration file, losing the table creation code.

### The Fix (Option A - Recommended)
1. **Reconstruct missing migration** `189b1231afd4` (creates all 16 tables)
2. **Rename mislabeled file** to `2a3f4c9d1cde_add_cascade_deletes.py`
3. **Test on fresh database**
4. **Proceed with manual testing**

**Estimated time:** 30-45 minutes

---

## Current Todo List

### Immediate Tasks (Before Script 03)
1. ⏳ **Fix habits_service missing base migration** (Option A implementation)
2. ⏳ **Test migrations manually** (habits + movements, then practices + users)
3. ⏳ **Add environment guards** to `metadata.create_all()` in all services
4. ⏳ **Run migration orchestration script** (03-run-migrations.sh)

### After Migrations Work
5. ⏳ **Update application code** for secret volume mounts (Python + Node.js)
6. ⏳ **Build and push Docker images** to Artifact Registry
7. ⏳ **Create env.production.tfvars** from example file
8. ⏳ **Run remaining bootstrap scripts** (04-apply-rls-policies.sh, 05-bootstrap-gcp.sh)
9. ⏳ **Initialize OpenTofu and deploy** infrastructure
10. ⏳ **Validate production deployment** (health checks, GraphQL, voucher flow)

---

## habits_service Schema (16 Tables to Create in Base Migration)

### Base Tables (No Foreign Keys)
1. **habit_templates** - Habit definitions (slug, title, description, etc.)
2. **lesson_templates** - Lesson content (markdown, segments, versioning)
3. **program_templates** - Program definitions (slug, title, versioning)

### Relationship Tables (With Foreign Keys)
4. **program_step_templates** - Steps in a program (→ program_templates, → habit_templates)
5. **step_lesson_templates** - Lessons for each step (→ program_step_templates, → lesson_templates)
6. **lesson_segments** - Lesson content chunks (→ lesson_templates)
7. **step_daily_plan** - Daily plan for each step (→ program_step_templates, → lesson_segments)

### User Data Tables
8. **user_program_assignments** - User enrollments (→ program_templates)
9. **habit_events** - Habit completion tracking (→ habit_templates, → user_program_assignments)
10. **lesson_events** - Lesson engagement tracking (→ lesson_templates, → user_program_assignments)
11. **journal_task_events** - Journal task tracking
12. **lesson_tasks** - Persistent lesson task instances (→ lesson_templates)

### ACL & Provenance Tables
13. **template_access** - Generic ACL (kind, template_id, user_id, permission)
14. **template_provenance** - Template origin metadata (system/user/import)

### Special Features in Models
- UUID primary keys (all tables)
- Timestamps with `func.now()` server defaults
- JSON columns (metadata, segments, tags)
- Unique constraints (composite keys like user_id + date)
- Check constraints (permission validation, kind validation)
- Foreign key behaviors (CASCADE, RESTRICT, SET NULL)

---

## Migration Chain (After Fix)

```
File: 189b1231afd4_bootstrap_tables.py
├─ revision: '189b1231afd4'
├─ down_revision: None
└─ Creates: All 16 tables + indexes + constraints

File: 2a3f4c9d1cde_add_cascade_deletes.py
├─ revision: '2a3f4c9d1cde'
├─ down_revision: '189b1231afd4'
└─ Modifies: FK constraints to CASCADE/RESTRICT

File: 3b7a1d2e4f56_soft_delete_program_templates.py
├─ revision: '3b7a1d2e4f56'
├─ down_revision: '2a3f4c9d1cde'
└─ Adds: is_deleted column + triggers + functions
```

---

## Key Commands Reference

### Check Migration Status
```bash
cd habits_service
poetry run alembic current    # Show current revision
poetry run alembic history    # Show all migrations
```

### Apply Migrations
```bash
poetry run alembic upgrade head       # Apply all pending
poetry run alembic upgrade +1         # Apply one migration
poetry run alembic upgrade <revision> # Apply to specific revision
```

### Create Migration
```bash
poetry run alembic revision --autogenerate -m "description"  # Auto-detect changes
poetry run alembic revision -m "description"                 # Manual migration
```

### Rollback
```bash
poetry run alembic downgrade -1         # Rollback one migration
poetry run alembic downgrade <revision> # Rollback to specific revision
```

### Dry Run
```bash
poetry run alembic upgrade head --sql   # Show SQL without executing
```

---

## Next Steps After `/clear`

1. **Implement Option A:**
   - Generate complete base migration file (189b1231afd4)
   - All 16 tables with proper schema, FKs, indexes, constraints
   - Rename existing file to correct revision (2a3f4c9d1cde)

2. **Test the fix:**
   - Spin up fresh database
   - Run `alembic upgrade head`
   - Verify all tables created

3. **Continue with manual testing:**
   - Follow ALEMBIC-MANUAL-TEST-PLAN.md
   - Test habits + movements
   - Generate initial migrations for practices + users
   - Run orchestration script

4. **Add environment guards:**
   - Update `metadata.create_all()` in all services
   - Production mode skips auto-create

5. **Proceed to production deployment**

---

## Files Created This Session

### Documentation
- `infra-v2/ALEMBIC-SETUP-GUIDE.md` (58KB) - Complete Alembic reference
- `infra-v2/ALEMBIC-MANUAL-TEST-PLAN.md` (15KB) - Step-by-step testing
- `infra-v2/ALEMBIC-WALKTHROUGH.md` (35KB) - End-to-end explanation
- `infra-v2/HABITS-SERVICE-ALEMBIC-FORENSICS.md` (25KB) - Gap analysis
- `infra-v2/READY-FOR-MIGRATIONS.md` (20KB) - Summary & action items
- `infra-v2/DATABASE-MIGRATION-RLS-REVIEW.md` (18KB) - Migration/RLS strategy
- `infra-v2/PHASE-2-RISK-ANALYSIS.md` (22KB) - VPC hardening deferral

### Alembic Configurations
- `practices_service/alembic/` (complete setup)
  - alembic.ini
  - alembic/env.py
  - alembic/script.py.mako
  - alembic/README
  - alembic/versions/__init__.py

- `users_service/alembic/` (complete setup)
  - alembic.ini
  - alembic/env.py
  - alembic/script.py.mako
  - alembic/README
  - alembic/versions/__init__.py

### Bug Fixes
- `meals_service/alembic/env.py` - Fixed deprecated `AsyncEngine()` constructor

---

## Environment Guards Pattern (To Implement)

```python
# Add to all services' database.py init_db() function:

import os

async def init_db():
    """Initialize database."""
    # Only auto-create in development
    if os.getenv("ENVIRONMENT", "development") == "development":
        async with engine.begin() as conn:
            await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "schema_name"'))
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created (development mode).")
    else:
        # Production: Use Alembic migrations
        print("Production mode: Skipping auto-create. Use Alembic migrations.")
```

**Files to update:**
- `practices_service/practices/repository/database.py:44`
- `users_service/users/repository/database.py:83`
- `meals_service/meals/repository/database.py:46`
- `habits_service/habits_service/app/main.py` (if present)

---

## Secret Volume Mount Pattern (To Implement)

**Python Services:**
```python
import os
from pathlib import Path

def read_secret(secret_name: str) -> str:
    """Read secret from volume mount or fall back to env var."""
    secret_path = Path(f"/secrets/{secret_name}/{secret_name}")

    if secret_path.exists():
        return secret_path.read_text().strip()

    # Fallback to env var for local development
    env_var_name = secret_name.upper().replace('-', '_')
    return os.getenv(env_var_name, '')

# Usage:
database_url = read_secret("database-url")  # Not os.getenv("DATABASE_URL")
```

**Gateway (Node.js):**
```javascript
const fs = require('fs');

function readSecret(secretName) {
  try {
    return fs.readFileSync(`/secrets/${secretName}/${secretName}`, 'utf8').trim();
  } catch (error) {
    return process.env[secretName.toUpperCase().replace(/-/g, '_')] || '';
  }
}

// Usage:
const supabaseJwtSecret = readSecret('supabase-jwt-secret');
```

---

## Key Insights

### Alembic Best Practices
1. **Always use --autogenerate** but **always review** generated files
2. **One logical change per migration** (not multiple unrelated changes)
3. **Test downgrade()** before deploying (ensure reversibility)
4. **Use meaningful migration messages** (not "update", "fix", "changes")
5. **Migrations are idempotent** - safe to run multiple times

### Migration Chain Integrity
- Alembic uses **revision IDs from file content**, not filenames
- Filenames are just for sorting/organization
- Each migration has `down_revision` pointing to parent
- Broken chain = deployment failure

### Production vs Development
- **Development:** `metadata.create_all()` is convenient
- **Production:** Must use Alembic migrations only
- **Environment guards** ensure production doesn't auto-create

### Schema Ownership
- Each service owns its schema (habits, meals, movements, etc.)
- 6 separate Alembic configs = correct microservices pattern
- Orchestration script handles all 6 automatically

---

## Estimated Timeline (From Current State)

### Immediate (Today)
- Fix habits_service migration: **45 mins**
- Manual testing (Phase 1-5): **40 mins**
- Add environment guards: **1 hour**
- **Total: ~2.5 hours**

### After Migrations Work
- Update app code for secrets: **1 hour**
- Build Docker images: **1 hour**
- Run bootstrap scripts: **2 hours**
- Deploy with OpenTofu: **1 hour**
- Validate deployment: **1 hour**
- **Total: ~6 hours**

### Grand Total: ~8.5 hours to production

---

## Questions Answered This Session

1. ✅ **How does Alembic work?** - Complete walkthrough with habits_service example
2. ✅ **What's the right pattern?** - One Alembic per service (microservices pattern)
3. ✅ **Is meals_service config correct?** - No, fixed deprecated API
4. ✅ **Are migrations idempotent?** - Yes, safe to run multiple times
5. ✅ **How to set up from scratch?** - Staff engineer approach documented
6. ✅ **What's wrong with habits_service?** - Missing base migration (forensic analysis complete)

---

## Copy-Paste This Summary After `/clear`

Paste this entire document to restore context, then continue with:

**Immediate next step:** Implement Option A (fix habits_service missing base migration)

**Command to continue:**
> "Let's implement Option A for habits_service. Please generate the missing base migration file (189b1231afd4) that creates all 16 tables from the SQLAlchemy models. Use the forensics document as reference."

---

**Session End.** Ready for compaction and continuation.
