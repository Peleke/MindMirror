# Epic: CLI Environment Management Improvements

**Status**: Ready for Implementation
**Priority**: High (blocks safe staging/prod seeding)
**Effort**: 2-3 hours
**Author**: Claude Code
**Date**: 2025-11-02

## 🎯 Epic Goal

Enable developers to seamlessly seed data across local/staging/production environments using simple, consistent commands without manually managing database URLs or risking environment confusion.

## 📋 User Stories

### Story 1: Environment-Aware Configuration
**As a** developer
**I want** to configure environment-specific settings once
**So that** I can switch between local/staging/prod without changing code

**Acceptance Criteria:**
- [ ] Environment vars follow pattern: `{ENV}_{SERVICE}_DATABASE_URL`
- [ ] Support `local`, `staging`, `production` environments
- [ ] Graceful fallback to sensible defaults
- [ ] Clear error messages when required vars missing

**Technical Details:**
```bash
# .env structure
LOCAL_DATABASE_URL="postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"
LOCAL_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://movements_user:movements_password@movements_postgres:5432/swae_movements"

STAGING_DATABASE_URL="postgresql+asyncpg://postgres:[pwd]@[staging-host]:5432/postgres"
STAGING_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[pwd]@[staging-host]:5432/postgres"

PRODUCTION_DATABASE_URL="postgresql+asyncpg://postgres:[pwd]@[prod-host]:5432/postgres"
PRODUCTION_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[pwd]@[prod-host]:5432/postgres"
```

---

### Story 2: Update Core Environment Utils
**As a** CLI framework
**I want** to support three distinct environments
**So that** all commands can safely target the correct infrastructure

**Acceptance Criteria:**
- [ ] Update `cli/src/mindmirror_cli/core/utils.py`
- [ ] Add `get_database_url()` helper with env-aware logic
- [ ] Add `is_production_environment()` safety check
- [ ] Deprecate binary `is_live_environment()` logic

**Files to Change:**
- `cli/src/mindmirror_cli/core/utils.py`

**Implementation:**
```python
def get_current_environment() -> str:
    """Get current environment: local, staging, or production."""
    return _current_environment

def is_production_environment() -> bool:
    """Check if targeting production (extra safety checks)."""
    return _current_environment == "production"

def get_database_url(service: str = "main") -> str:
    """
    Get database URL for service based on environment.

    Args:
        service: 'main' (habits/journal), 'movements', 'practices', 'users'

    Returns:
        Database URL string

    Examples:
        get_database_url('main') with env=staging
        -> STAGING_DATABASE_URL

        get_database_url('movements') with env=production
        -> PRODUCTION_MOVEMENTS_DATABASE_URL
    """
    env = _current_environment.upper()

    # Service-specific URL mapping
    service_env_map = {
        'main': f'{env}_DATABASE_URL',
        'movements': f'{env}_MOVEMENTS_DATABASE_URL',
        'practices': f'{env}_PRACTICES_DATABASE_URL',
        'users': f'{env}_USERS_DATABASE_URL',
    }

    env_var = service_env_map.get(service, f'{env}_DATABASE_URL')
    url = os.getenv(env_var)

    if not url:
        # Fallback to legacy SUPABASE_DATABASE_URL for backwards compat
        if env in ['STAGING', 'PRODUCTION']:
            url = os.getenv('SUPABASE_DATABASE_URL')

    if not url and env == 'LOCAL':
        # Docker compose defaults
        if service == 'movements':
            return "postgresql+asyncpg://movements_user:movements_password@movements_postgres:5432/swae_movements"
        elif service == 'practices':
            return "postgresql+asyncpg://practices_user:practices_password@practices_postgres:5432/swae_practices"
        elif service == 'users':
            return "postgresql+asyncpg://users_user:users_password@users_postgres:5432/swae_users"
        else:
            return "postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach"

    if not url:
        raise ValueError(
            f"Missing database URL for {service} service in {_current_environment} environment. "
            f"Set {env_var} environment variable."
        )

    return url
```

---

### Story 3: Update Seed Habits Command
**As a** developer
**I want** `seed-habits` to support all three environments
**So that** I can seed habits data consistently everywhere

**Acceptance Criteria:**
- [ ] Accept `--env local|staging|production`
- [ ] Use `get_database_url('main')` helper
- [ ] Add production safety confirmation prompt
- [ ] Update CLI help text

**Files to Change:**
- `cli/src/mindmirror_cli/commands/seed_habits.py`

**Implementation:**
```python
async def _run():
    if env:
        set_environment(env)
        console.print(f"[blue]Environment: {get_current_environment()}[/blue]")

    # Production safety check
    if is_production_environment():
        confirm = typer.confirm(
            "⚠️  You are seeding PRODUCTION. Continue?",
            default=False
        )
        if not confirm:
            raise typer.Exit(0)

    # Get database URL using helper
    if not database_url:
        database_url = get_database_url('main')

    console.print(f"[cyan]Target DB:[/cyan] {database_url.split('@')[-1]}")
    # ... rest of implementation
```

---

### Story 4: Update Seed Movements Commands
**As a** developer
**I want** both `seed-movements` and `seed-pn-movements` to support all environments
**So that** I can populate movements data safely

**Acceptance Criteria:**
- [ ] Both commands accept `--env local|staging|production`
- [ ] Use `get_database_url('movements')` helper
- [ ] Production safety prompts
- [ ] Consistent error messages

**Files to Change:**
- `cli/src/mindmirror_cli/commands/seed_movements.py`
- `cli/src/mindmirror_cli/commands/seed_pn_movements.py`

**Implementation Pattern:**
```python
async def _execute(...):
    if env:
        set_environment(env)

    if is_production_environment():
        # Safety prompt
        ...

    if not database_url:
        database_url = get_database_url('movements')

    # ... rest
```

---

### Story 5: Documentation & Testing
**As a** developer
**I want** clear documentation and examples
**So that** I can confidently seed any environment

**Acceptance Criteria:**
- [ ] Update `cli/README.md` with environment examples
- [ ] Create `.env.example` with all environment templates
- [ ] Test seeding in local environment
- [ ] Document staging/production setup process

**Deliverables:**
1. Updated README with examples:
```bash
# Local (Docker)
poetry run mindmirror seed-habits run /data/programs/my-program --env local

# Staging
export STAGING_DATABASE_URL="..."
poetry run mindmirror seed-habits run /data/programs/my-program --env staging

# Production (with safety prompt)
export PRODUCTION_DATABASE_URL="..."
poetry run mindmirror seed-habits run /data/programs/my-program --env production
```

2. `.env.example`:
```bash
# === Local Environment (Docker Compose defaults) ===
# No configuration needed - automatic defaults

# === Staging Environment ===
STAGING_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"
STAGING_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"

# === Production Environment ===
PRODUCTION_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"
PRODUCTION_MOVEMENTS_DATABASE_URL="postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres"
```

---

## 🏗️ Implementation Plan

### Phase 1: Core Infrastructure (Story 1 + 2)
**Time**: 45 mins
1. Update `utils.py` with new helpers
2. Add environment validation
3. Test environment switching

### Phase 2: Command Updates (Story 3 + 4)
**Time**: 60 mins
1. Update `seed_habits.py`
2. Update `seed_movements.py`
3. Update `seed_pn_movements.py`
4. Add production safety prompts

### Phase 3: Documentation & Testing (Story 5)
**Time**: 30 mins
1. Update CLI README
2. Create `.env.example`
3. Test all three environments
4. Verify safety prompts work

**Total Estimated Time**: 2-3 hours

---

## 🧪 Testing Checklist

### Local Environment
- [ ] `seed-habits --env local` works without env vars
- [ ] `seed-movements --env local` uses Docker compose defaults
- [ ] `seed-pn-movements --env local` connects to local DB

### Staging Environment
- [ ] `seed-habits --env staging` requires STAGING_DATABASE_URL
- [ ] Clear error if STAGING_DATABASE_URL missing
- [ ] Successful seed with correct env vars

### Production Environment
- [ ] `seed-habits --env production` shows safety prompt
- [ ] Can cancel production seed
- [ ] Requires PRODUCTION_DATABASE_URL
- [ ] Successful seed after confirmation

### Safety & Validation
- [ ] Invalid `--env` shows helpful error
- [ ] Missing database URL shows which var to set
- [ ] Production prompts can't be bypassed accidentally

---

## 📊 Success Metrics

1. **Developer Experience**: Single command works across all environments
2. **Safety**: Zero accidental production seeds
3. **Configuration**: One-time env var setup per environment
4. **Consistency**: All seed commands follow same pattern

---

## 🚀 Future Enhancements (Out of Scope)

- [ ] Add `--dry-run` flag for preview
- [ ] Support environment profiles (`.env.staging`, `.env.production`)
- [ ] Add seed rollback/undo capability
- [ ] Seed status/version tracking

---

## 📝 Notes

- **Backwards Compatibility**: Fallback to `SUPABASE_DATABASE_URL` for legacy setups
- **Schema Support**: Maintains existing `--schema` flag for flexibility
- **Explicit Overrides**: `--db-url` still works for one-off cases
- **Docker Integration**: Local defaults aligned with `docker-compose.yml`
