# 🧹 Celery Removal Plan: Complete Legacy Cleanup

## 📋 Executive Summary

Since there's no legacy system running (the old setup never worked), we can completely remove Celery infrastructure and simplify to a single Pub/Sub-based task processor. This document outlines the complete cleanup plan.

---

## 🎯 Goals
- **Remove all Celery dependencies** and infrastructure
- **Simplify to single FastAPI service** with Pub/Sub endpoints
- **Eliminate Redis dependency** (if only used for Celery)
- **Clean up legacy code** and configuration
- **Maintain 100% functionality** with new Pub/Sub architecture

---

## 🏗️ Current State Analysis

### **What We Have**
- ✅ **Pub/Sub Infrastructure**: Topics, subscriptions, dead letter queues
- ✅ **Task Processors**: Direct business logic execution
- ✅ **Pub/Sub Endpoints**: HTTP push subscription handlers
- ✅ **Legacy Endpoints**: Deprecated Celery queue endpoints
- ✅ **Dual-Mode Container**: Web (FastAPI) + Worker (Celery) modes

### **What We Can Remove**
- ❌ **Celery App**: `celery_app.py` and all Celery configuration
- ❌ **Celery Tasks**: All task definitions in `src/tasks/`
- ❌ **Redis Dependency**: If only used for Celery
- ❌ **Worker Mode**: No need for separate Celery worker
- ❌ **Legacy Endpoints**: Deprecated queue endpoints
- ❌ **Dual-Mode Logic**: `RUN_MODE` environment variable

---

## 🧹 Phase-by-Phase Cleanup Plan

### **Phase 1: Remove Celery Infrastructure**

#### **A. Remove Celery Dependencies**
**File**: `celery-worker/pyproject.toml`
```toml
# REMOVE these dependencies:
celery = "^5.3.0"
redis = "^4.6.0"
pytest-celery = "^4.0.0"
```

#### **B. Remove Celery Files**
```bash
# Files to DELETE:
celery-worker/src/celery_app.py
celery-worker/start-worker.sh
celery-worker/src/tasks/  # Entire directory
```

#### **C. Remove Celery Configuration**
**File**: `celery-worker/src/app.py`
- Remove `RUN_MODE` environment variable logic
- Remove conditional app creation
- Remove Celery imports
- Always create FastAPI app

### **Phase 2: Simplify Container Setup**

#### **A. Update Dockerfile**
**File**: `celery-worker/Dockerfile`
```dockerfile
# REMOVE:
# - start-worker.sh reference
# - Celery-related setup

# SIMPLIFY to:
CMD ["./start.sh"]  # Single startup script
```

#### **B. Update Startup Scripts**
**File**: `celery-worker/start-web.sh` → `celery-worker/start.sh`
```bash
#!/bin/bash
echo "Starting Task Processor service..."
exec uvicorn src.app:app --host 0.0.0.0 --port 8000
```

#### **C. Update App Structure**
**File**: `celery-worker/src/app.py`
```python
# REMOVE:
# - RUN_MODE logic
# - Conditional app creation
# - Celery imports

# SIMPLIFY to:
app = create_app()  # Always create FastAPI app
```

### **Phase 3: Update Infrastructure**

#### **A. Terraform Changes**
**File**: `infra/modules/celery-worker/main.tf`
```hcl
# REMOVE:
# - celery_worker service (keep only celery_worker_web)
# - Redis-related resources
# - Celery-specific IAM permissions

# RENAME:
# - celery_worker_web → task-processor
# - Update all references
```

#### **B. Environment Variables**
**Files**: Various Terraform files
```hcl
# REMOVE these env vars:
# - REDIS_URL
# - RUN_MODE
# - TASK_DEFAULT_RETRY_DELAY (Celery-specific)
# - TASK_MAX_RETRIES (Celery-specific)
# - TASK_TIME_LIMIT (Celery-specific)

# KEEP these env vars:
# - All Pub/Sub topics/subscriptions
# - Service URLs
# - Database/Qdrant configs
# - Security keys
```

### **Phase 4: Update Service Integration**

#### **A. Update Service Calls**
**Files**: Various service files
- Remove calls to Celery worker service
- Update service discovery to use single task processor
- Update health checks

#### **B. Update Tests**
**Files**: `celery-worker/tests/`
```bash
# REMOVE:
# - test_tasks.py (legacy Celery tests)
# - test_celery_app.py
# - Celery-related test fixtures

# KEEP:
# - test_task_processors.py
# - test_pubsub_client.py
# - test_message_processing.py
# - test_basic.py (Pub/Sub endpoints)
```

### **Phase 5: Code Cleanup**

#### **A. Remove Legacy Endpoints**
**File**: `celery-worker/src/app.py`
```python
# REMOVE these endpoints:
# - @app.post("/tasks/index-journal-entry")
# - @app.post("/tasks/reindex-tradition")

# KEEP these endpoints:
# - @app.post("/pubsub/journal-indexing")
# - @app.post("/pubsub/tradition-rebuild")
# - @app.get("/health")
```

#### **B. Remove Legacy Functions**
**Files**: Various task files
```python
# REMOVE these functions:
# - queue_journal_entry_indexing()
# - queue_tradition_reindex()
# - All Celery task decorators

# KEEP these functions:
# - publish_journal_indexing_message()
# - publish_tradition_rebuild_message()
# - All task processor functions
```

#### **C. Update Imports**
**Files**: Throughout codebase
```python
# REMOVE imports:
# - from celery import Celery
# - from src.celery_app import celery_app
# - from src.tasks.journal_tasks import queue_journal_entry_indexing

# KEEP imports:
# - from src.clients.pubsub_client import get_pubsub_client
# - from src.tasks.task_processors import get_journal_processor
```

### **Phase 6: Documentation Updates**

#### **A. Update README**
**File**: `celery-worker/README.md`
- Remove Celery setup instructions
- Update deployment instructions
- Update architecture diagrams
- Add Pub/Sub architecture explanation

#### **B. Update Docker Compose**
**File**: `docker-compose.yml`
```yaml
# REMOVE:
# - redis service
# - celery-worker service (if separate)

# UPDATE:
# - Simplify to single task-processor service
# - Remove Redis environment variables
# - Update service dependencies
```

### **Phase 7: Final Cleanup**

#### **A. Remove Unused Files**
```bash
# Files to check and potentially remove:
# - Any Celery configuration files
# - Redis configuration files
# - Legacy task definition files
# - Unused test fixtures
```

#### **B. Update Project Structure**
```bash
# CONSIDER renaming:
# - celery-worker/ → task-processor/
# - Update all references in:
#   - Terraform files
#   - Docker Compose
#   - CI/CD pipelines
#   - Documentation
```

---

## 🔧 Implementation Strategy

### **Recommended Order**
1. **Phase 1**: Remove Celery dependencies and files
2. **Phase 2**: Simplify container setup
3. **Phase 3**: Update infrastructure (Terraform)
4. **Phase 4**: Update service integration
5. **Phase 5**: Code cleanup
6. **Phase 6**: Documentation updates
7. **Phase 7**: Final cleanup

### **Testing Strategy**
- **After each phase**: Run tests to ensure nothing breaks
- **Integration testing**: Test Pub/Sub message flow
- **End-to-end testing**: Test complete workflows
- **Performance testing**: Verify no performance regression

### **Rollback Plan**
- **Git branches**: Work on feature branch
- **Docker tags**: Keep old container images
- **Terraform state**: Can rollback infrastructure changes
- **Gradual deployment**: Deploy changes incrementally

---

## ✅ Success Criteria

### **Functional Requirements**
- ✅ All Pub/Sub message processing works
- ✅ All task processor functions work
- ✅ Health checks pass
- ✅ No performance regression
- ✅ Zero downtime during transition

### **Code Quality**
- ✅ No Celery dependencies remain
- ✅ No Redis dependencies (if only for Celery)
- ✅ Clean, simplified codebase
- ✅ Comprehensive test coverage
- ✅ Updated documentation

### **Infrastructure**
- ✅ Single Cloud Run service
- ✅ Simplified Terraform configuration
- ✅ Reduced resource usage
- ✅ Cleaner service architecture

---

## 🚀 Benefits After Cleanup

### **Operational Benefits**
- **Simplified deployment**: Single service to manage
- **Reduced complexity**: No dual-mode logic
- **Lower resource usage**: No Redis dependency
- **Easier debugging**: Single codebase to understand

### **Development Benefits**
- **Faster builds**: Fewer dependencies
- **Cleaner code**: No legacy code to maintain
- **Better testing**: Simpler test setup
- **Easier onboarding**: Less complexity for new developers

### **Cost Benefits**
- **Reduced infrastructure**: No Redis instance
- **Lower compute costs**: Single service instead of two
- **Simplified monitoring**: Fewer services to monitor

---

## 📋 Checklist

### **Phase 1: Celery Infrastructure**
- [ ] Remove Celery dependencies from pyproject.toml
- [ ] Delete celery_app.py
- [ ] Delete start-worker.sh
- [ ] Delete src/tasks/ directory
- [ ] Remove RUN_MODE logic from app.py

### **Phase 2: Container Setup**
- [ ] Update Dockerfile
- [ ] Rename start-web.sh to start.sh
- [ ] Simplify app.py to always create FastAPI app
- [ ] Remove Celery imports

### **Phase 3: Infrastructure**
- [ ] Update Terraform to single service
- [ ] Remove Redis environment variables
- [ ] Remove Celery-specific IAM permissions
- [ ] Update service names and references

### **Phase 4: Service Integration**
- [ ] Update service calls
- [ ] Remove Celery-related tests
- [ ] Update test fixtures
- [ ] Verify health checks

### **Phase 5: Code Cleanup**
- [ ] Remove legacy endpoints
- [ ] Remove legacy functions
- [ ] Clean up imports
- [ ] Remove unused files

### **Phase 6: Documentation**
- [ ] Update README
- [ ] Update Docker Compose
- [ ] Update architecture diagrams
- [ ] Update deployment guides

### **Phase 7: Final Cleanup**
- [ ] Remove unused files
- [ ] Consider renaming directories
- [ ] Update CI/CD pipelines
- [ ] Final testing and validation

---

This cleanup will result in a much simpler, more maintainable codebase focused purely on Pub/Sub-based task processing. 