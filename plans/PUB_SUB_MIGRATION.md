# Celery → Google Cloud Pub/Sub Migration Plan

## Overview

This document outlines the complete migration from Celery to Google Cloud Pub/Sub for the MindMirror indexing and processing system. This migration will eliminate Redis dependencies, improve scalability, and provide better native GCP integration.

## Current Architecture

- **celery-worker**: FastAPI web service + Celery worker (mixed process)
- **agent_service**: Calls celery-worker web API for task queuing
- **journal_service**: Calls celery-worker web API for task queuing
- **Redis**: Message broker for Celery
- **Tasks**: Journal indexing, tradition rebuilding, health checks

## Target Architecture

- **celery-worker-web**: FastAPI service that publishes to Pub/Sub
- **celery-worker**: Pub/Sub subscriber service (separate process)
- **agent_service**: Calls celery-worker-web API (no changes to interface)
- **journal_service**: Calls celery-worker-web API (no changes to interface)
- **Pub/Sub**: Message broker with topics and subscriptions
- **Handlers**: Async message processors for each task type

---

## Phase1frastructure Setup

### 1.1ate Pub/Sub Topics & Subscriptions

**Topics:**
- `journal-indexing` - Single journal entry indexing
- `journal-batch-indexing` - Batch journal entry indexing  
- `journal-reindex` - User reindexing operations
- `tradition-rebuild` - Tradition knowledge base rebuilds
- `health-check` - Health monitoring tasks

**Subscriptions:**
- `journal-indexing-sub` (with dead letter topic)
- `journal-batch-indexing-sub` (with dead letter topic)
- `journal-reindex-sub` (with dead letter topic)
- `tradition-rebuild-sub` (with dead letter topic)
- `health-check-sub` (with dead letter topic)

**Dead Letter Topics:**
- `journal-indexing-dlq`
- `journal-batch-indexing-dlq`
- `journal-reindex-dlq`
- `tradition-rebuild-dlq`
- `health-check-dlq`

### 1.2orm Infrastructure

**Files to modify:**
- `infra/modules/celery-worker/main.tf`
- `infra/modules/celery-worker/variables.tf`
- `infra/modules/celery-worker/outputs.tf`

**Changes:**
- Add Pub/Sub topic and subscription resources
- Remove Redis dependencies
- Update service account permissions for Pub/Sub
- Remove worker service (keep only web service)
- Add Pub/Sub publisher and subscriber permissions

---

## Phase2es & Configuration

### 2.1 Update Dependencies

**Files to modify:**
- `celery-worker/pyproject.toml`

**Remove:**
```toml
celery = "^5.3.0
redis =^5.00
pytest-celery =<=1.10
```

**Add:**
```toml
google-cloud-pubsub = "^2.18
google-cloud-logging = ^30.8``

### 2.2/Sub Configuration

**New file:**
- `celery-worker/src/pubsub_config.py`

**Contents:**
- Topic names and subscription configurations
- Environment variables for project ID
- Retry and dead letter queue settings
- Message routing configuration

---

## Phase 3: Core Business Logic Migration

### 3.1 Extract Task Logic

**Files to create:**
- `celery-worker/src/handlers/journal_handlers.py`
- `celery-worker/src/handlers/tradition_handlers.py`
- `celery-worker/src/handlers/health_handlers.py`

**Logic to move:**
- `index_journal_entry_by_id()` → `handle_index_journal_entry()`
- `JournalIndexer` class → `journal_handlers.py`
- `rebuild_tradition_knowledge_base()` → `handle_rebuild_tradition()`
- Health check logic → `handle_health_check()`

### 3.2te Pub/Sub Message Handlers

**Handler functions:**
- `handle_index_journal_entry(message)` - Process single entry indexing
- `handle_batch_index_entries(message)` - Process batch indexing
- `handle_reindex_user_entries(message)` - Process user reindexing
- `handle_rebuild_tradition(message)` - Process tradition rebuilds
- `handle_health_check(message)` - Process health checks

---

## Phase 4: Message Publishing (Web Service)

### 4.1 Update Web Service

**Files to modify:**
- `celery-worker/src/app.py`

**Changes:**
- Replace Celery task calls with Pub/Sub message publishing
- Update queue functions to publish functions
- Add Pub/Sub publisher client initialization

### 4.2Message Publishers

**Files to create:**
- `celery-worker/src/publishers/journal_publisher.py`
- `celery-worker/src/publishers/tradition_publisher.py`

**Publisher functions:**
- `publish_index_journal_entry(entry_id, user_id, tradition)`
- `publish_batch_index_entries(entries_data)`
- `publish_reindex_user_entries(user_id, tradition)`
- `publish_rebuild_tradition(tradition)`

---

## Phase 5: Message Processing (Worker Service)

### 5.1ate Pub/Sub Worker Service

**New file:**
- `celery-worker/src/worker.py`

**Features:**
- Pub/Sub subscriber with message routing
- Error handling and retry logic
- Dead letter queue processing
- Graceful shutdown handling

### 5.2 Update Entry Points

**Files to modify:**
- `celery-worker/start-worker.sh`
- `celery-worker/Dockerfile`

**Changes:**
- Replace Celery worker with Pub/Sub subscriber
- Remove Celery-specific environment variables
- Add Pub/Sub configuration

---

## Phase 6: Data Models & Serialization

### 6.1ate Message Models

**New file:**
- `celery-worker/src/models/pubsub_models.py`

**Models:**
- `IndexJournalEntryMessage`
- `BatchIndexEntriesMessage`
- `ReindexUserMessage`
- `RebuildTraditionMessage`
- `HealthCheckMessage`

### 6.2sage Serialization

**Implementation:**
- JSON serialization/deserialization for Pub/Sub messages
- Base64 encoding for binary data if needed
- Message validation using Pydantic models

---

## Phase7: Error Handling & Monitoring

###70.1lement Retry Logic

**Features:**
- Pub/Sub built-in retries + custom retry logic
- Dead letter topics for failed messages
- Exponential backoff for transient failures
- Message acknowledgment strategies

### 7.2 Update Monitoring

**Changes:**
- Replace Celery monitoring with Pub/Sub metrics
- Cloud Logging integration
- Custom metrics for processing times
- Error tracking and alerting

---

## Phase 8: Testing & Migration

### 81ate Tests

**Files to modify:**
- `celery-worker/tests/`
- `celery-worker/pyproject.toml`

**Changes:**
- Replace `pytest-celery` with Pub/Sub emulator
- Update integration tests to use Pub/Sub
- Mock Pub/Sub for unit tests
- Add end-to-end testing

### 8.2 Migration Strategy

**Steps:**
1Deploy new Pub/Sub infrastructure alongside existing Celery
2. Gradually migrate traffic from Celery to Pub/Sub
3tor for any issues
4. Remove Celery infrastructure once stable

---

## Phase 9: Cleanup

###90.1elery Dependencies

**Files to delete/modify:**
- Delete `celery-worker/src/celery_app.py`
- Remove Celery-specific code from tasks
- Update documentation
- Remove Redis configuration

---

## Changes Required in Other Services

### Agent Service Changes

**Files to modify:**
- `src/agent_service/clients/task_client.py`
- `src/agent_service/app/api/hooks.py`

**Changes:**
- No interface changes needed (still calls web API)
- Update `CELERY_WORKER_URL` to point to new web service
- Ensure proper error handling for new response format

### Journal Service Changes

**Files to modify:**
- `src/journal_service/journal_service/app/config.py`

**Changes:**
- No interface changes needed (still calls web API)
- Update `CELERY_WORKER_URL` to point to new web service
- Ensure proper error handling for new response format

### Infrastructure Changes

**Files to modify:**
- `docker-compose.yml`
- `infra/main.tf`
- `infra/variables.tf`

**Changes:**
- Remove Redis service from docker-compose
- Update service dependencies
- Remove Celery worker service
- Update environment variables

---

## Implementation Timeline

### Week1: Infrastructure & Core Setup
- **Days 1**: Set up Pub/Sub topics and subscriptions
- **Days 3-4: Update Terraform and dependencies
- **Day5: Create basic Pub/Sub configuration

### Week2ss Logic Migration
- **Days 1xtract and migrate task logic to handlers
- **Days 4-5**: Create message publishers and update web service

### Week3: Worker Service & Testing
- **Days 1**: Create Pub/Sub worker service
- **Days 3-4: Update tests and add monitoring
- **Day 5**: End-to-end testing

### Week 4: Deployment & Cleanup
- **Days1eploy and validate in staging
- **Days3duction deployment and monitoring
- **Day 5**: Cleanup Celery infrastructure

---

## Benefits of Migration

### Technical Benefits
- ✅ **Native GCP Integration**: No more Redis dependency
- ✅ **Better Scalability**: Pub/Sub auto-scales with load
- ✅ **Reliability**: Built-in retries, dead letter queues
- ✅ **Monitoring**: Native Cloud Monitoring integration
- ✅ **Cost**: Pay per message, not for idle workers
- ✅ **Simplicity**: No more process management issues

### Operational Benefits
- ✅ **Reduced Infrastructure**: One less service to manage
- ✅ **Better Observability**: Native GCP logging and monitoring
- ✅ **Easier Debugging**: Pub/Sub message inspection
- ✅ **Fault Tolerance**: Automatic retries and dead letter queues

---

## Risk Mitigation

### Rollback Plan
- Keep Celery infrastructure running during migration
- Gradual traffic migration with monitoring
- Ability to quickly switch back to Celery if needed

### Testing Strategy
- Comprehensive unit and integration tests
- Load testing with Pub/Sub
- End-to-end testing with real data
- Monitoring and alerting setup

### Data Consistency
- Ensure no messages are lost during migration
- Validate processing results match between systems
- Monitor for any data inconsistencies

---

## Success Criteria

1**Functionality**: All existing tasks work correctly with Pub/Sub
2. **Performance**: Processing times are equivalent or better
3. **Reliability**: No message loss and proper error handling
4Monitoring**: Full observability of the new system
5. **Cost**: Reduced infrastructure costs
6. **Maintenance**: Simplified operational overhead

---

## Next Steps

1. Review and approve this migration plan
2. Set up development environment with Pub/Sub emulator
3. Begin Phase 1 implementation
4. Regular progress reviews and adjustments
5. Production deployment with monitoring 