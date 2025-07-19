# Supabase CLI Integration Plan

## Overview

This plan outlines the implementation of a `supabase` subcommand for the MindMirror CLI that wraps Alembic for database migration management. The implementation will be staff-level, production-ready, and follow TDD principles.

## Current CLI Structure Analysis

Based on the existing CLI structure:
- **Main app**: `cli/src/mindmirror_cli/main.py` - Uses Typer with subcommand pattern
- **Subcommands**: `cli/src/mindmirror_cli/commands/` - Contains `qdrant.py` as reference
- **Core logic**: `cli/src/mindmirror_cli/core/` - Contains business logic and clients
- **Dependencies**: Uses `typer`, `rich`, async patterns, and proper error handling

## Directory Layout

```
repo-root/
├── alembic/                    # NEW: Alembic configuration and migrations
│   ├── env.py                  # Alembic environment configuration
│   ├── versions/               # Migration files
│   └── README.md              # Migration guidelines
├── alembic.ini                # NEW: Alembic configuration file
├── cli/
│   └── src/mindmirror_cli/
│       ├── commands/
│       │   ├── qdrant.py      # Existing
│       │   └── supabase.py    # NEW: Supabase subcommand
│       ├── core/
│       │   ├── supabase_client.py  # NEW: Supabase connection logic
│       │   └── alembic_manager.py  # NEW: Alembic orchestration
│       └── utils/
│           └── db_utils.py    # NEW: Database utilities
└── src/
    ├── agent_service/
    ├── journal_service/
    └── shared/
        └── data_models.py     # SQLAlchemy models
```

## Implementation Phases

### Phase 1: Foundation Setup (TDD First)

#### 1.1 Alembic Configuration
- [ ] Create `alembic.ini` with environment variable support
- [ ] Create `alembic/env.py` with proper SQLAlchemy integration
- [ ] Add Alembic dependencies to `cli/pyproject.toml`
- [ ] Create initial migration structure

#### 1.2 Core Infrastructure
- [ ] Create `cli/src/mindmirror_cli/core/supabase_client.py`
  - Database connection management
  - Health check functionality
  - Environment variable handling
- [ ] Create `cli/src/mindmirror_cli/core/alembic_manager.py`
  - Alembic command orchestration
  - Migration state management
  - Error handling and validation

#### 1.3 CLI Subcommand Structure
- [ ] Create `cli/src/mindmirror_cli/commands/supabase.py`
  - Follow existing `qdrant.py` patterns
  - Implement all required commands
  - Add proper error handling and rich output

### Phase 2: Command Implementation

#### 2.1 Core Commands
- [ ] `mindmirror supabase init` - Bootstrap database
- [ ] `mindmirror supabase revision "message"` - Create migrations
- [ ] `mindmirror supabase upgrade` - Apply migrations
- [ ] `mindmirror supabase downgrade <rev>` - Rollback migrations
- [ ] `mindmirror supabase status` - Show migration status
- [ ] `mindmirror supabase history` - Show migration history

#### 2.2 Advanced Commands
- [ ] `mindmirror supabase reset` - Destructive reset (with confirmation)
- [ ] `mindmirror supabase health` - Database health check
- [ ] `mindmirror supabase validate` - Validate migration state

### Phase 3: Testing & Validation

#### 3.1 Unit Tests
- [ ] Test `supabase_client.py` with mocked connections
- [ ] Test `alembic_manager.py` with mocked Alembic operations
- [ ] Test CLI commands with mocked dependencies
- [ ] Test error handling scenarios

#### 3.2 Integration Tests
- [ ] Test with local Postgres instance
- [ ] Test with Supabase emulator
- [ ] Test migration workflows end-to-end
- [ ] Test environment variable handling

#### 3.3 E2E Tests
- [ ] Test complete database bootstrap workflow
- [ ] Test migration creation and application
- [ ] Test rollback scenarios
- [ ] Test error recovery

## Detailed Command Specifications

### `mindmirror supabase init`
**Purpose**: Bootstrap database with initial schema
**Behavior**:
- Check if `alembic_version` table exists
- If not exists: create initial migration + upgrade to head
- If exists: abort with clear message
- Validate database connection before proceeding
- Show progress with rich output

**TDD Test Cases**:
```python
def test_init_fresh_database():
    # Test successful initialization of fresh database
    
def test_init_existing_database():
    # Test abort when database already initialized
    
def test_init_connection_failure():
    # Test handling of database connection failures
```

### `mindmirror supabase revision "message"`
**Purpose**: Create new migration from model changes
**Behavior**:
- Validate database connection
- Run `alembic revision --autogenerate -m "message"`
- Show generated migration file path
- Validate migration file content
- Option to open migration file for review

**TDD Test Cases**:
```python
def test_revision_creates_migration():
    # Test successful migration creation
    
def test_revision_no_changes():
    # Test handling when no model changes detected
    
def test_revision_invalid_message():
    # Test validation of migration message
```

### `mindmirror supabase upgrade`
**Purpose**: Apply pending migrations
**Behavior**:
- Show current migration status
- List pending migrations
- Apply migrations with progress indication
- Show final status
- Handle upgrade failures gracefully

**TDD Test Cases**:
```python
def test_upgrade_applies_pending_migrations():
    # Test successful migration application
    
def test_upgrade_no_pending_migrations():
    # Test when no migrations to apply
    
def test_upgrade_failure_handling():
    # Test handling of migration failures
```

### `mindmirror supabase downgrade <rev>`
**Purpose**: Rollback to specific migration
**Behavior**:
- Validate revision exists
- Show what will be rolled back
- Confirm destructive operation
- Execute rollback with progress
- Show final status

**TDD Test Cases**:
```python
def test_downgrade_to_valid_revision():
    # Test successful rollback
    
def test_downgrade_invalid_revision():
    # Test handling of invalid revision
    
def test_downgrade_confirmation():
    # Test confirmation prompt behavior
```

### `mindmirror supabase status`
**Purpose**: Show current migration status
**Behavior**:
- Display current revision
- Show pending migrations
- Show migration history
- Display database connection status

**TDD Test Cases**:
```python
def test_status_shows_current_revision():
    # Test status display
    
def test_status_no_migrations():
    # Test status with no migrations
```

### `mindmirror supabase reset`
**Purpose**: Destructive database reset
**Behavior**:
- Show warning about data loss
- Require explicit confirmation
- Drop and recreate database
- Re-run initial migration
- Show reset completion status

**TDD Test Cases**:
```python
def test_reset_with_confirmation():
    # Test successful reset with confirmation
    
def test_reset_aborted():
    # Test reset when user cancels
```

## Environment Configuration

### Required Environment Variables
```bash
# Database connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mindmirror
DB_USER=postgres
DB_PASS=password

# Optional: Schema configuration
DB_SCHEMA=mindmirror
```

### alembic.ini Configuration
```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+psycopg2://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME
```

## Dependencies to Add

### CLI Dependencies (`cli/pyproject.toml`)
```toml
[tool.poetry.dependencies]
# Existing dependencies...
alembic = "^1.13.0"
psycopg2-binary = "^2.9.0"
sqlalchemy = "^2.0.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
# Existing dev dependencies...
pytest-postgresql = "^4.1.0"
testcontainers = "^3.7.0"
```

## Testing Strategy

### Test Environment Setup
1. **Unit Tests**: Mock all external dependencies
2. **Integration Tests**: Use `pytest-postgresql` for local Postgres
3. **E2E Tests**: Use Testcontainers for isolated Postgres instances

### Test Data Management
- Use fixtures for database state
- Clean up after each test
- Use transaction rollbacks for isolation

### Migration Testing
- Test migration creation
- Test migration application
- Test migration rollback
- Test migration validation

## Implementation Sequence

### Step 1: Foundation (Week 1)
1. Set up Alembic configuration
2. Create core infrastructure classes
3. Add basic CLI subcommand structure
4. Write initial tests

### Step 2: Core Commands (Week 2)
1. Implement `init` command
2. Implement `revision` command
3. Implement `upgrade` command
4. Add comprehensive tests

### Step 3: Advanced Features (Week 3)
1. Implement `downgrade` command
2. Implement `status` and `history` commands
3. Implement `reset` command with safety
4. Add integration tests

### Step 4: Polish & Documentation (Week 4)
1. Add error handling and validation
2. Improve user experience with rich output
3. Write documentation and examples
4. Final testing and validation

## Success Criteria

### Functional Requirements
- [ ] All commands work as specified
- [ ] Proper error handling and user feedback
- [ ] Idempotent operations where appropriate
- [ ] Safe destructive operations with confirmation

### Quality Requirements
- [ ] 90%+ test coverage
- [ ] All tests pass in CI/CD
- [ ] Documentation complete
- [ ] Follows existing CLI patterns

### Production Readiness
- [ ] Environment variable configuration
- [ ] Logging and monitoring support
- [ ] Error recovery mechanisms
- [ ] Security best practices

## Risk Mitigation

### Technical Risks
- **Database connection issues**: Implement robust connection handling
- **Migration conflicts**: Add validation and conflict resolution
- **Environment differences**: Use environment-specific configurations

### Operational Risks
- **Data loss**: Implement confirmation prompts for destructive operations
- **Migration failures**: Add rollback mechanisms and validation
- **Performance issues**: Monitor migration performance and optimize

## Future Enhancements

### Phase 2 Features (Post-MVP)
- [ ] Migration templates for common patterns
- [ ] Automated migration testing
- [ ] Migration performance monitoring
- [ ] Integration with CI/CD pipelines
- [ ] Multi-database support
- [ ] Migration dependency management

### Advanced Features
- [ ] Migration preview mode
- [ ] Automated migration suggestions
- [ ] Migration performance optimization
- [ ] Database schema visualization
- [ ] Migration rollback planning

## Recommended Usage Sequence

### Initial Setup
```bash
# 1. Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=mindmirror
export DB_USER=postgres
export DB_PASS=password

# 2. Initialize database
mindmirror supabase init

# 3. Verify status
mindmirror supabase status
```

### Ongoing Development
```bash
# 1. Make model changes in src/shared/data_models.py

# 2. Create migration
mindmirror supabase revision "add user table"

# 3. Review generated migration file
# (manually edit if needed)

# 4. Apply migration
mindmirror supabase upgrade

# 5. Verify status
mindmirror supabase status
```

### Troubleshooting
```bash
# Check database health
mindmirror supabase health

# View migration history
mindmirror supabase history

# Rollback if needed
mindmirror supabase downgrade <revision>

# Reset if necessary (destructive)
mindmirror supabase reset
```

This plan provides a comprehensive, TDD-oriented approach to implementing the Supabase CLI subcommand with Alembic integration, following the existing CLI patterns and ensuring production-ready quality. 