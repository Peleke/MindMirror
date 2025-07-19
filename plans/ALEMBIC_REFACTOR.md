# Alembic Refactoring Plan: Clean Separation & Proper Packaging

## 🎯 Overview

Refactor the current Alembic setup to achieve clean separation of concerns, proper packaging, and eliminate path manipulation and circular import hazards.

## 🧱 Current Problems

- CLI tool is overly aware of service internals
- Path manipulation and `sys.path` hacks
- Circular import hazards between CLI and services
- Alembic configuration tightly coupled to CLI
- No reusable Alembic package for other tools/services

## ✅ Goals

1. **CLI Service-Agnostic**: CLI should not know about service model internals
2. **Clean Imports**: No `sys.path` manipulation or PYTHONPATH hacks
3. **Reusable Alembic Config**: Package Alembic configuration for distribution
4. **Modular Model Loading**: Support multiple services without tight coupling
5. **Proper Packaging**: Make Alembic config installable and distributable

## 📋 Detailed Implementation Plan

### Phase 1: Create Central Models Aggregator

#### 1.1 Create `src/models/` Package Structure
- [ ] Create directory: `src/models/`
- [ ] Create `src/models/__init__.py`
- [ ] Create `src/models/README.md` with usage documentation
- [ ] Add `src/models/` to `.gitignore` exclusions (if needed)

#### 1.2 Implement Central Metadata Aggregator
- [ ] Import `Base` from `journal_service.models.sql.base`
- [ ] Import `Base` from `agent_service.models.sql.base` (if exists)
- [ ] Import all model classes from each service
- [ ] Create combined metadata object
- [ ] Handle schema conflicts (e.g., same table names across services)
- [ ] Export single `metadata` object for external use
- [ ] Add error handling for missing services/models

#### 1.3 Test Model Aggregation
- [ ] Verify all journal service models are included
- [ ] Verify all agent service models are included (if any)
- [ ] Test schema conflict resolution
- [ ] Ensure metadata contains all expected tables
- [ ] Add unit tests for model aggregation

### Phase 2: Package Alembic as Installable Package

#### 2.1 Create `alembic-config` Package Structure
```
alembic-config/
├── pyproject.toml
├── README.md
├── alembic_config/
│   ├── __init__.py
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── __init__.py
└── setup.py (if needed)
```

#### 2.2 Package Configuration Files
- [ ] Create `alembic-config/pyproject.toml`
  - [ ] Set package name: `alembic-config`
  - [ ] Set version: `0.1.0`
  - [ ] Add description and authors
  - [ ] Include `alembic_config` package
  - [ ] Add dependencies: `alembic`, `sqlalchemy`, `python-dotenv`
- [ ] Create `alembic-config/README.md`
- [ ] Create `alembic-config/alembic_config/__init__.py`

#### 2.3 Migrate Alembic Files
- [ ] Move `alembic/env.py` → `alembic-config/alembic_config/env.py`
- [ ] Move `alembic/script.py.mako` → `alembic-config/alembic_config/script.py.mako`
- [ ] Create `alembic-config/alembic_config/versions/__init__.py`
- [ ] Update `env.py` to import from `src.models` cleanly
- [ ] Remove all path manipulation from `env.py`
- [ ] Ensure environment variable loading works correctly

#### 2.4 Update Alembic Configuration
- [ ] Update `env.py` to import `metadata` from `src.models`
- [ ] Set `target_metadata = metadata`
- [ ] Remove `sys.path.append()` calls
- [ ] Remove `PYTHONPATH` manipulation
- [ ] Test that model imports work correctly

### Phase 3: Install and Integrate with CLI

#### 3.1 Add Package to CLI Dependencies
- [ ] Add `alembic-config` as local dependency in `cli/pyproject.toml`
- [ ] Use path dependency: `alembic-config = {path = "../alembic-config"}`
- [ ] Run `poetry install` to install the package
- [ ] Verify package is installed correctly

#### 3.2 Update CLI to Use Package
- [ ] Update `cli/generate_initial_migration.py` to use installed package
- [ ] Remove direct `alembic/` directory references
- [ ] Update any hardcoded paths to use package imports
- [ ] Test that CLI can find and use the package

#### 3.3 Remove Old Alembic Directory
- [ ] Remove `alembic/` directory from repo root
- [ ] Update `.gitignore` if needed
- [ ] Verify no references remain to old directory

### Phase 4: Clean Up CLI Dependencies

#### 4.1 Remove Service Awareness from CLI
- [ ] Remove `PYTHONPATH` manipulation from `generate_initial_migration.py`
- [ ] Remove direct model imports from CLI scripts
- [ ] Remove `sys.path.append()` calls
- [ ] Ensure CLI only knows about:
  - [ ] Environment variables
  - [ ] Alembic commands
  - [ ] Database connection parameters

#### 4.2 Simplify Migration Script
- [ ] Update `cli/generate_initial_migration.py`
- [ ] Remove model import logic
- [ ] Remove path manipulation
- [ ] Focus only on:
  - [ ] Environment switching
  - [ ] Alembic command orchestration
  - [ ] Migration file modification
- [ ] Let `alembic-config` handle all model/metadata concerns

#### 4.3 Update CLI Core Files
- [ ] Update `cli/src/mindmirror_cli/core/supabase_client.py`
- [ ] Remove any model-related imports
- [ ] Ensure only database connection logic remains
- [ ] Update `cli/src/mindmirror_cli/core/alembic_manager.py`
- [ ] Remove model awareness
- [ ] Focus on Alembic command execution

### Phase 5: Update Alembic Configuration

#### 5.1 Update `alembic.ini`
- [ ] Update `script_location` to point to installed package
- [ ] Set `script_location = alembic_config`
- [ ] Remove any hardcoded paths
- [ ] Ensure environment variable interpolation works
- [ ] Test configuration is valid

#### 5.2 Finalize `alembic-config/env.py`
- [ ] Import `metadata` from `src.models`
- [ ] Set `target_metadata = metadata`
- [ ] Remove all path manipulation
- [ ] Handle environment variable loading properly
- [ ] Add proper error handling
- [ ] Add logging for debugging

### Phase 6: Testing & Validation

#### 6.1 Test Package Installation
- [ ] Install `alembic-config` in development mode
- [ ] Verify CLI can find and use the package
- [ ] Test `poetry install` works correctly
- [ ] Verify package imports work

#### 6.2 Test Model Aggregation
- [ ] Verify all journal service models are included
- [ ] Verify all agent service models are included (if any)
- [ ] Test schema conflicts are handled properly
- [ ] Ensure migration generation includes all tables
- [ ] Test with different service combinations

#### 6.3 Test End-to-End Migration Flow
- [ ] Test `mindmirror supabase init` works
- [ ] Test `mindmirror supabase revision` works
- [ ] Test `mindmirror supabase upgrade` works
- [ ] Test `mindmirror supabase status` works
- [ ] Test `mindmirror supabase health` works

#### 6.4 Test Local Database Migration Generation
- [ ] Test `python generate_initial_migration.py` works
- [ ] Verify migration files are generated correctly
- [ ] Verify schema modifications are applied
- [ ] Test migration application to Supabase

### Phase 7: Documentation & Cleanup

#### 7.1 Update Documentation
- [ ] Update `cli/README.md` with new architecture
- [ ] Update `alembic-config/README.md`
- [ ] Update `src/models/README.md`
- [ ] Add usage examples
- [ ] Document the new separation of concerns

#### 7.2 Code Cleanup
- [ ] Remove unused imports
- [ ] Remove commented-out code
- [ ] Update type hints where needed
- [ ] Add proper error messages
- [ ] Ensure consistent code style

#### 7.3 Final Validation
- [ ] Run all CLI commands successfully
- [ ] Generate and apply migrations successfully
- [ ] Verify no circular imports
- [ ] Verify no path manipulation
- [ ] Test in clean environment

## 🚀 Benefits After Refactoring

### For CLI
- **Service-Agnostic**: No knowledge of internal model structure
- **Simpler Code**: Focus only on orchestration and user interaction
- **Easier Testing**: No complex setup required
- **Better Maintainability**: Clear separation of concerns

### For Alembic Config
- **Reusable**: Can be used by other tools/services
- **Installable**: Proper Python package with dependencies
- **Distributable**: Can be published to artifact registry
- **Versioned**: Proper version management

### For Models
- **Centralized**: Single source of truth for all models
- **Composable**: Easy to add/remove services
- **Testable**: Can test model aggregation independently
- **Documented**: Clear API for external consumers

### For Development
- **No Path Hacks**: Everything uses proper Python imports
- **Clear Dependencies**: Explicit dependency management
- **Better DX**: Easier to understand and modify
- **Future-Proof**: Ready for proper packaging and distribution

## 🎯 Success Criteria

- [ ] CLI can run all commands without service awareness
- [ ] Alembic config is installable as a package
- [ ] All models are properly aggregated in `src/models`
- [ ] No `sys.path` manipulation or PYTHONPATH hacks
- [ ] End-to-end migration flow works correctly
- [ ] Package can be distributed to artifact registry
- [ ] Documentation is complete and accurate

## 🔄 Next Steps After Refactoring

1. **Deploy to Supabase**: Apply migrations to production database
2. **Set up Qdrant**: Configure vector database for production
3. **Deploy Services**: Deploy to Cloud Run for public access
4. **Monitor & Iterate**: Gather feedback and improve

---

**Note**: This refactoring maintains the existing CLI command structure while achieving clean separation of concerns and proper packaging. 