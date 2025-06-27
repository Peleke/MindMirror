# Comprehensive Test Plan for Prompt System

## Overview
This document outlines the complete testing strategy for the prompt system implementation, including unit tests, integration tests, and end-to-end validation.

## 🧪 Test Categories

### 1. Unit Tests (Core Components)

#### 1.1 Model Tests
```bash
# Test data models and validation
poetry run python -m pytest src/agent_service/tests/test_prompt_models.py -v
```
**Coverage**: PromptInfo, PromptConfig, PromptStats, StorageConfig validation

#### 1.2 Storage Loader Tests
```bash
# Test storage abstraction layer
poetry run python -m pytest src/agent_service/tests/test_storage_loaders.py -v
```
**Coverage**: LocalStorageLoader, GCSStorageLoader, StorageLoader protocol

#### 1.3 Prompt Store Tests
```bash
# Test individual storage implementations
poetry run python -m pytest src/agent_service/tests/test_inmemory_prompt_store.py -v
poetry run python -m pytest src/agent_service/tests/test_local_prompt_store.py -v
poetry run python -m pytest src/agent_service/tests/test_gcs_prompt_store.py -v
```
**Coverage**: All storage backends with error handling and edge cases

#### 1.4 Service Layer Tests
```bash
# Test service orchestration
poetry run python -m pytest src/agent_service/tests/test_prompt_service.py -v
poetry run python -m pytest src/agent_service/tests/test_prompt_registry.py -v
poetry run python -m pytest src/agent_service/tests/test_prompt_factory.py -v
```
**Coverage**: Service logic, caching, registry operations

### 2. Integration Tests

#### 2.1 Storage Integration Tests
```bash
# Test storage backends with real file operations
poetry run python -m pytest src/agent_service/tests/test_storage_integration.py -v
```
**Coverage**: End-to-end storage operations, file persistence, YAML serialization

#### 2.2 Service Integration Tests
```bash
# Test service with real storage backends
poetry run python -m pytest src/agent_service/tests/test_service_integration.py -v
```
**Coverage**: Service with different storage backends, caching behavior

### 3. Docker Integration Tests

#### 3.1 Container Tests
```bash
# Test the system running in Docker containers
docker-compose up -d
poetry run python -m pytest src/agent_service/tests/test_docker_integration.py -v
docker-compose down
```
**Coverage**: Container startup, volume mounting, environment variables

#### 3.2 GCS Emulator Tests
```bash
# Test with GCS emulator
docker-compose --profile development up -d gcs-emulator
poetry run python -m pytest src/agent_service/tests/test_gcs_emulator.py -v
docker-compose --profile development down
```
**Coverage**: GCS operations with local emulator

### 4. End-to-End Tests

#### 4.1 Full System Tests
```bash
# Test complete system with all services
docker-compose up -d
poetry run python -m pytest src/agent_service/tests/test_e2e_prompts.py -v
docker-compose down
```
**Coverage**: Complete prompt lifecycle, API endpoints, GraphQL integration

#### 4.2 Performance Tests
```bash
# Test system performance under load
poetry run python -m pytest src/agent_service/tests/test_performance.py -v
```
**Coverage**: Response times, concurrent access, memory usage

## 🚀 Test Execution Commands

### Quick Test Suite (Development)
```bash
# Run all unit tests
poetry run python -m pytest src/agent_service/tests/ -v -m "not integration" --tb=short

# Run specific component tests
poetry run python -m pytest src/agent_service/tests/test_prompt_models.py -v
poetry run python -m pytest src/agent_service/tests/test_storage_loaders.py -v
poetry run python -m pytest src/agent_service/tests/test_local_prompt_store.py -v
poetry run python -m pytest src/agent_service/tests/test_gcs_prompt_store.py -v
```

### Full Integration Test Suite
```bash
# Start services
docker-compose up -d

# Run integration tests
poetry run python -m pytest src/agent_service/tests/ -v -m "integration"

# Run end-to-end tests
poetry run python -m pytest src/agent_service/tests/test_e2e_prompts.py -v

# Cleanup
docker-compose down
```

### GCS Emulator Tests
```bash
# Start GCS emulator
docker-compose --profile development up -d gcs-emulator

# Run GCS tests
poetry run python -m pytest src/agent_service/tests/test_gcs_emulator.py -v

# Cleanup
docker-compose --profile development down
```

## 📊 Test Coverage Goals

### Unit Tests: 95%+ Coverage
- **Models**: 100% (validation, serialization, edge cases)
- **Storage Loaders**: 95%+ (all methods, error handling)
- **Prompt Stores**: 95%+ (CRUD operations, error scenarios)
- **Services**: 95%+ (business logic, caching)

### Integration Tests: 100% Coverage
- **Storage Backends**: All storage types with real operations
- **Service Integration**: Service with all storage backends
- **Docker Integration**: Container startup and configuration

### End-to-End Tests: Critical Paths
- **API Endpoints**: All prompt-related endpoints
- **GraphQL Integration**: Query and mutation operations
- **Performance**: Response time benchmarks

## 🔧 Test Environment Setup

### Local Development
```bash
# Install dependencies
poetry install

# Set up test environment
export PROMPT_STORAGE_TYPE=local
export PROMPT_STORAGE_LOCAL_PATH=/tmp/test_prompts

# Run tests
poetry run python -m pytest src/agent_service/tests/ -v
```

### Docker Environment
```bash
# Start services with test configuration
docker-compose up -d

# Run tests against running services
poetry run python -m pytest src/agent_service/tests/test_docker_integration.py -v

# Cleanup
docker-compose down
```

### GCS Emulator Environment
```bash
# Start GCS emulator
docker-compose --profile development up -d gcs-emulator

# Configure for GCS emulator
export PROMPT_STORAGE_TYPE=gcs
export PROMPT_STORAGE_GCS_BUCKET=test-bucket
export STORAGE_EMULATOR_HOST=localhost:4443

# Run GCS tests
poetry run python -m pytest src/agent_service/tests/test_gcs_emulator.py -v

# Cleanup
docker-compose --profile development down
```

## 🎯 Test Scenarios

### 1. Basic CRUD Operations
- Create, read, update, delete prompts
- Version management
- Metadata handling
- Variable extraction

### 2. Storage Backend Switching
- Local → GCS migration
- GCS → Local fallback
- Configuration validation
- Error handling

### 3. Performance Scenarios
- Large prompt collections (10k+ prompts)
- Concurrent access
- Cache hit/miss scenarios
- Memory usage optimization

### 4. Error Scenarios
- Network failures (GCS)
- File system errors (local)
- Invalid configurations
- Corrupted data handling

### 5. Integration Scenarios
- API endpoint testing
- GraphQL query/mutation testing
- Service health checks
- Docker container communication

## 📈 Success Metrics

### Performance Benchmarks
- **Prompt Retrieval**: <100ms (cached), <500ms (uncached)
- **Storage Operations**: <1s for large files
- **Concurrent Access**: 100+ concurrent requests
- **Memory Usage**: <512MB per service instance

### Reliability Metrics
- **Test Coverage**: >95% unit test coverage
- **Error Rate**: <1% for core operations
- **Recovery Time**: <30s for service restart
- **Data Integrity**: 100% data consistency

### Integration Metrics
- **API Response Time**: <2s for complex operations
- **GraphQL Performance**: <1s for queries
- **Docker Startup**: <60s for all services
- **Health Check**: 100% service availability

## 🚨 Troubleshooting

### Common Test Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Permission Errors**: Check file system permissions for local storage
3. **Network Errors**: Verify Docker network connectivity
4. **Timeout Errors**: Increase timeout values for slow operations

### Debug Commands
```bash
# Check service logs
docker-compose logs agent_service

# Check GCS emulator logs
docker-compose logs gcs-emulator

# Test storage connectivity
docker exec agent_service python -c "from agent_service.llms.prompts.stores import LocalPromptStore; print('Storage OK')"

# Check environment variables
docker exec agent_service env | grep PROMPT
```

## 📝 Test Documentation

### Test Reports
- **Coverage Reports**: `poetry run coverage report`
- **Performance Reports**: `poetry run pytest --benchmark-only`
- **Integration Reports**: `poetry run pytest --html=reports/integration.html`

### Continuous Integration
- **GitHub Actions**: Automated test execution
- **Docker Build**: Test container builds
- **Deployment**: Test deployment pipelines

---

## 🎯 Next Steps

1. **Run Unit Tests**: Verify all components work independently
2. **Run Integration Tests**: Test component interactions
3. **Run Docker Tests**: Verify container deployment
4. **Run E2E Tests**: Validate complete system functionality
5. **Performance Testing**: Benchmark system performance
6. **Documentation**: Update deployment and usage guides 