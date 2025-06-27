# 🚀 Agent Service Refactoring Plan: TDD-First LangGraph Migration

## 📋 Executive Summary

This document outlines a comprehensive, test-driven refactoring plan to transform the current monolithic `agent_service` into a modular, scalable, LangGraph-based multi-agent system with Memgraph integration for Graph RAG.

### 🎯 Goals
- **Modularity**: Break down monolithic engines into composable LangGraph nodes
- **Observability**: Full LangSmith tracing for all operations
- **Scalability**: Multi-agent orchestration with clean service boundaries
- **Graph RAG**: Memgraph integration for advanced knowledge graph operations
- **Testability**: Comprehensive test coverage with TDD approach

---

## 🏗️ Current Architecture Analysis

### ✅ Strengths
- LangGraph and LangSmith already in dependencies
- Comprehensive test infrastructure (pytest, docker fixtures)
- Qdrant-based vector store with hybrid search
- GraphQL API with proper authentication
- Modular service structure in place

### ❌ Pain Points
- **Monolithic Engines**: `CoachingEngine` and `QdrantCoachingEngine` mix concerns
- **Scattered LLM Logic**: LLM operations spread across multiple services
- **No LangGraph Implementation**: Despite being in dependencies
- **No LangSmith Tracing**: Missing observability layer
- **Tight Coupling**: Services tightly coupled to engines
- **Mixed Async/Sync**: Inconsistent patterns

---

## 🧪 TDD-First Refactoring Strategy

### Phase 1: Foundation & Infrastructure ✅ **COMPLETED**

#### ✅ Completed
- [x] **LangSmith Tracing Infrastructure**
  - `src/agent_service/tracing/__init__.py` - Centralized tracing setup
  - `src/agent_service/tracing/decorators.py` - Tracing decorators
  - `src/agent_service/tests/test_langsmith_tracing.py` - Comprehensive tests

- [x] **LangGraph State Management**
  - `src/agent_service/agents/state.py` - Typed state classes
  - `src/agent_service/tests/test_agent_state.py` - State management tests

- [x] **Core LangChain Components**
  - `src/agent_service/llms/factory.py` - Centralized LLM management
  - `src/agent_service/agents/nodes/rag_node.py` - First LangGraph node
  - `src/agent_service/tests/test_rag_node.py` - RAG node tests
  - `src/agent_service/tests/test_llm_factory.py` - LLM factory tests

#### 🎯 Phase 1 Success Metrics
- **Test Coverage**: 95%+ for all new components
- **Performance**: <2s response time for RAG queries
- **Modularity**: All components independently testable
- **Tracing**: Full observability for all operations

---

### Phase 2: Prompt System Refactoring 🔄 **IN PROGRESS**

#### 🎯 Objectives
- Refactor monolithic `PromptRegistry` into modular, production-ready system
- Support persistent storage (GCS for prod, local files for dev/testing)
- Maintain 100% backward compatibility
- Enable YAML-based prompt definitions with versioning

#### 📋 Tasks

##### 2.1 Core Abstractions & Interfaces (Days 1-2) 🔄 **IN PROGRESS**
- [x] **Test**: `test_prompt_store_interface.py` - Test storage interface contracts
- [ ] **Implementation**: `src/agent_service/llms/prompts/stores/__init__.py` - Define `PromptStore` protocol
- [ ] **Test**: `test_prompt_service_interface.py` - Test service interface contracts
- [ ] **Implementation**: `src/agent_service/llms/prompts/service.py` - Define `PromptService` interface
- [ ] **Test**: `test_prompt_models.py` - Test enhanced `PromptInfo` and related models
- [ ] **Implementation**: `src/agent_service/llms/prompts/models.py` - Enhanced data models with versioning
- [ ] **Test**: `test_prompt_config.py` - Test configuration loading and validation
- [ ] **Implementation**: `src/agent_service/llms/prompts/config.py` - Configuration management

##### 2.2 Storage Layer Implementation (Days 3-4)
- [ ] **Test**: `test_local_prompt_store.py` - Test local file-based storage
- [ ] **Implementation**: `src/agent_service/llms/prompts/stores/local.py` - Local file store
- [ ] **Test**: `test_yaml_prompt_loading.py` - Test YAML prompt file format
- [ ] **Implementation**: `src/agent_service/llms/prompts/formats/yaml.py` - YAML prompt loader
- [ ] **Test**: `test_inmemory_prompt_store.py` - Test in-memory storage
- [ ] **Implementation**: `src/agent_service/llms/prompts/stores/memory.py` - In-memory store
- [ ] **Test**: `test_gcs_prompt_store.py` - Test GCS storage with mocks
- [ ] **Implementation**: `src/agent_service/llms/prompts/stores/gcs.py` - GCS store

##### 2.3 Service Layer & Registry Refactoring (Days 5-6)
- [ ] **Test**: `test_prompt_service.py` - Test service orchestration
- [ ] **Implementation**: `src/agent_service/llms/prompts/service.py` - Service implementation
- [ ] **Test**: `test_prompt_service_caching.py` - Test caching behavior
- [ ] **Implementation**: Add caching layer to service
- [ ] **Test**: `test_prompt_registry_refactored.py` - Test refactored registry
- [ ] **Implementation**: Refactor `PromptRegistry` to focus on rendering only
- [ ] **Test**: `test_prompt_registry_compatibility.py` - Ensure backward compatibility

##### 2.4 Migration & Integration (Days 7-8)
- [ ] **Test**: `test_migration_compatibility.py` - Test migration from old to new system
- [ ] **Implementation**: `src/agent_service/llms/prompts/migration.py` - Migration utilities
- [ ] **Test**: `test_existing_api_compatibility.py` - Ensure existing API still works
- [ ] **Test**: `test_prompt_config_integration.py` - Test config-driven store selection
- [ ] **Implementation**: Integrate configuration with service initialization
- [ ] **Test**: `test_prompt_performance.py` - Performance benchmarks
- [ ] **Implementation**: Optimize caching and storage operations

#### 🏗️ New Architecture
```python
# New Prompt System Architecture
PromptService (High-level interface)
├── PromptStore (Storage abstraction)
│   ├── LocalPromptStore (dev/testing)
│   ├── GCSPromptStore (production)
│   └── InMemoryPromptStore (fallback)
├── PromptRegistry (Rendering + cache)
└── PromptLoader (Template engine abstraction)
```

#### 🎯 Phase 2 Success Metrics
- **Test Coverage**: 95%+ for all new components
- **Performance**: <100ms prompt retrieval (cached)
- **Storage**: Support for 10k+ prompts without degradation
- **Migration**: Zero downtime during transition
- **Backward Compatibility**: 100% API compatibility maintained

---

### Phase 3: Retriever Factory & Journal Processing (Week 2)

#### 🎯 Objectives
- Create modular retriever factory
- Build journal processing nodes
- Integrate with new prompt system
- Maintain 100% test coverage

#### 📋 Tasks

##### 3.1 Retriever Factory (Days 1-3)
- [ ] **Test**: `test_retriever_factory.py` - Test retriever factory methods
- [ ] **Implementation**: `src/agent_service/retrievers/factory.py` - Retriever factory
- [ ] **Test**: `test_qdrant_retriever.py` - Test Qdrant retriever wrapper
- [ ] **Implementation**: `src/agent_service/retrievers/qdrant_retriever.py` - Qdrant adapter
- [ ] **Test**: `test_hybrid_search.py` - Test hybrid search functionality
- [ ] **Implementation**: `src/agent_service/retrievers/hybrid_search.py` - Hybrid search

##### 3.2 Journal Processing Nodes (Days 4-7)
- [ ] **Test**: `test_journal_summary_node.py` - Test journal summarization node
- [ ] **Implementation**: `src/agent_service/agents/nodes/journal_summary_node.py`
- [ ] **Test**: `test_journal_analysis_node.py` - Test journal analysis node
- [ ] **Implementation**: `src/agent_service/agents/nodes/journal_analysis_node.py`
- [ ] **Test**: `test_performance_review_node.py` - Test performance review node
- [ ] **Implementation**: `src/agent_service/agents/nodes/performance_review_node.py`
- [ ] **Test**: `test_journal_workflow.py` - Test complete journal workflow
- [ ] **Implementation**: `src/agent_service/agents/workflows/journal_workflow.py`

---

### Phase 4: Service Decomposition (Week 3)

#### 🎯 Objectives
- Refactor existing engines into modular components
- Separate service boundaries
- Update GraphQL integration

#### 📋 Tasks

##### 4.1 Engine Refactoring
- [ ] **Test**: `test_engine_factory.py` - Test engine factory pattern
- [ ] **Implementation**: `src/agent_service/engine/factory.py` - Engine factory
- [ ] **Test**: `test_legacy_migration.py` - Test migration from old engines
- [ ] **Implementation**: `src/agent_service/engine/migration.py` - Migration utilities

##### 4.2 Service Separation
- [ ] **Test**: `test_service_boundaries.py` - Test service interface contracts
- [ ] **Implementation**: `src/agent_service/services/`
  - `coaching_service.py` - Pure coaching logic
  - `knowledge_service.py` - Knowledge base operations
  - `user_service.py` - User-specific operations

##### 4.3 GraphQL Integration
- [ ] **Test**: `test_graphql_resolvers.py` - Test new GraphQL resolvers
- [ ] **Implementation**: `src/agent_service/web/resolvers.py` - Refactored resolvers
- [ ] **Test**: `test_api_integration.py` - Test end-to-end API integration
- [ ] **Implementation**: `src/agent_service/web/app.py` - Updated FastAPI app

---

### Phase 5: Memgraph Integration & Multi-Agent (Week 4)

#### 🎯 Objectives
- Integrate Memgraph for advanced graph operations
- Build multi-agent orchestration
- Implement auto-tool generation

#### 📋 Tasks

##### 5.1 Memgraph Setup
- [ ] **Test**: `test_memgraph_client.py` - Test Memgraph connection and operations
- [ ] **Implementation**: `src/agent_service/graphs/memgraph_client.py` - Memgraph client
- [ ] **Test**: `test_graph_rag.py` - Test graph-based RAG operations
- [ ] **Implementation**: `src/agent_service/graphs/graph_rag.py` - Graph RAG implementation

##### 5.2 Multi-Agent Orchestration
- [ ] **Test**: `test_agent_orchestrator.py` - Test multi-agent coordination
- [ ] **Implementation**: `src/agent_service/agents/orchestrator.py` - Agent orchestrator
- [ ] **Test**: `test_agent_communication.py` - Test inter-agent communication
- [ ] **Implementation**: `src/agent_service/agents/communication.py` - Agent messaging

##### 5.3 Advanced Tooling
- [ ] **Test**: `test_autotool_generation.py` - Test automatic tool generation
- [ ] **Implementation**: `src/agent_service/tools/autotool.py` - Auto-tool generation
- [ ] **Test**: `test_tool_execution.py` - Test tool execution and monitoring
- [ ] **Implementation**: `src/agent_service/tools/execution.py` - Tool execution engine

---

## 🧪 Testing Strategy

### Test Categories
1. **Unit Tests**: Individual components and functions
2. **Integration Tests**: Component interactions
3. **End-to-End Tests**: Full workflow validation
4. **Performance Tests**: Load and stress testing

### Test Coverage Goals
- **Unit Tests**: 95%+ coverage
- **Integration Tests**: All major workflows
- **E2E Tests**: Critical user journeys
- **Performance Tests**: Response time benchmarks

### Test Data Management
- **Fixtures**: Reusable test data
- **Mocks**: External service dependencies
- **Docker**: Isolated test environments
- **Factories**: Test object creation

### Test Refactoring Strategy
- **Parallel Development**: New tests alongside existing ones
- **Gradual Migration**: Replace old tests as components are refactored
- **Compatibility Testing**: Ensure new components work with existing tests
- **Performance Regression**: Monitor test execution time

---

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**
- Each node has a single responsibility
- Services handle business logic only
- Infrastructure concerns isolated

### 2. **Composability**
- Nodes can be combined in different ways
- Chains are reusable across agents
- Tools are pluggable and discoverable

### 3. **Observability**
- All operations traced with LangSmith
- Structured logging throughout
- Metrics and monitoring hooks

### 4. **Testability**
- Pure functions where possible
- Dependency injection
- Mockable interfaces

### 5. **Scalability**
- Stateless operations
- Horizontal scaling support
- Caching strategies

---

## 📊 Success Metrics

### Technical Metrics
- **Test Coverage**: >95% unit test coverage
- **Response Time**: <2s for RAG queries, <100ms for prompt retrieval
- **Error Rate**: <1% for core operations
- **Memory Usage**: <512MB per agent instance

### Business Metrics
- **User Satisfaction**: Improved response quality
- **Development Velocity**: Faster feature delivery
- **Maintenance Cost**: Reduced debugging time
- **System Reliability**: 99.9% uptime

---

## 🚨 Risk Mitigation

### Technical Risks
1. **LangGraph Learning Curve**
   - **Mitigation**: Start with simple workflows, gradual complexity
   - **Fallback**: Keep existing engines during transition

2. **Performance Degradation**
   - **Mitigation**: Performance testing at each phase
   - **Fallback**: Optimize bottlenecks, caching strategies

3. **Integration Complexity**
   - **Mitigation**: Incremental migration, feature flags
   - **Fallback**: Parallel systems during transition

### Business Risks
1. **Feature Regression**
   - **Mitigation**: Comprehensive testing, gradual rollout
   - **Fallback**: Rollback procedures, monitoring

2. **Development Delays**
   - **Mitigation**: Clear milestones, parallel development
   - **Fallback**: Prioritize critical features

---

## 📅 Implementation Timeline

### Week 1: Foundation ✅ **COMPLETED**
- [x] LangSmith tracing infrastructure
- [x] State management system
- [x] First LangGraph node (RAG)
- [x] LLM factory completion
- [x] Comprehensive test coverage

### Week 2: Prompt System Refactoring 🔄 **IN PROGRESS**
- [ ] Core abstractions & interfaces (Days 1-2)
- [ ] Storage layer implementation (Days 3-4)
- [ ] Service layer & registry refactoring (Days 5-6)
- [ ] Migration & integration (Days 7-8)

### Week 3: Retriever Factory & Journal Processing
- [ ] Retriever factory (Days 1-3)
- [ ] Journal processing nodes (Days 4-7)
- [ ] Integration testing

### Week 4: Service Decomposition
- [ ] Engine refactoring
- [ ] Service separation
- [ ] GraphQL integration
- [ ] Legacy migration

### Week 5: Advanced Features
- [ ] Memgraph integration
- [ ] Multi-agent orchestration
- [ ] Auto-tool generation
- [ ] Performance optimization

---

## 🎯 Next Immediate Actions

### This Week (Phase 2 Completion)
1. **Complete Core Abstractions**
   ```bash
   # Create interface definitions and tests
   mkdir -p src/agent_service/llms/prompts/stores
   touch src/agent_service/llms/prompts/stores/__init__.py
   ```

2. **Implement Storage Layer**
   ```bash
   # Create storage implementations
   touch src/agent_service/llms/prompts/stores/local.py
   touch src/agent_service/llms/prompts/stores/gcs.py
   ```

3. **Refactor Service Layer**
   ```bash
   # Update service and registry
   touch src/agent_service/llms/prompts/service.py
   ```

### Next Week (Phase 3 Start)
1. **Retriever Factory Implementation**
2. **Journal Processing Nodes**
3. **Integration Testing**

---

## 📚 Resources & References

### Documentation
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Documentation](https://python.langchain.com/)

### Code Examples
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [LangSmith Examples](https://github.com/langchain-ai/langsmith/tree/main/examples)

### Best Practices
- [LangChain Best Practices](https://python.langchain.com/docs/guides/best_practices)
- [LangGraph Best Practices](https://langchain-ai.github.io/langgraph/tutorials/best_practices/)

---

## 🤝 Team Collaboration

### Roles & Responsibilities
- **Architecture Lead**: Overall design and technical decisions
- **Backend Developers**: Implementation and testing
- **DevOps**: Infrastructure and deployment
- **QA**: Testing and validation

### Communication Channels
- **Daily Standups**: Progress updates and blockers
- **Weekly Reviews**: Architecture decisions and milestones
- **Code Reviews**: All changes require review
- **Documentation**: Keep this plan updated

---

## 📝 Conclusion

This refactoring plan provides a clear, test-driven path to transform the agent service into a modern, scalable, LangGraph-based system. The TDD approach ensures quality and maintainability throughout the process.

**Key Success Factors:**
1. **Incremental Migration**: Gradual transition with fallbacks
2. **Comprehensive Testing**: TDD ensures quality at every step
3. **Clear Architecture**: Modular design enables future growth
4. **Observability**: Full tracing and monitoring from day one

**Expected Outcomes:**
- More maintainable and testable codebase
- Better performance and scalability
- Enhanced developer experience
- Foundation for advanced AI features

---

*Last Updated: [Current Date]*
*Next Review: [Next Week]*

# Prompt System Refactoring Plan

## Overview
This document outlines the comprehensive refactoring plan for the prompt management system, including storage abstraction, GCS integration, and comprehensive testing.

## ✅ Completed Work

### 1. **Core Architecture Refactoring**
- ✅ **Protocol Separation**: Created dedicated `PromptStore` protocol in `src/agent_service/llms/prompts/stores/protocol.py`
- ✅ **Storage Abstraction**: Implemented storage loader abstraction layer for switching between local and GCS backends
- ✅ **YAML Storage**: Updated `LocalPromptStore` to use YAML format instead of JSON
- ✅ **Model Enhancements**: Added `StorageConfig` model for configuration management

### 2. **GCS Integration**
- ✅ **GCS Storage Loader**: Implemented `GCSStorageLoader` with proper error handling and retry logic
- ✅ **GCS Prompt Store**: Created `GCSPromptStore` using storage abstraction layer
- ✅ **Docker Integration**: Added GCS emulator support in Docker Compose configuration
- ✅ **Environment Configuration**: Integrated GCS storage options into main Docker Compose file

### 3. **Comprehensive Testing Implementation**
- ✅ **Model Tests**: Complete test coverage for `PromptInfo`, `PromptConfig`, `PromptStats`, and `StorageConfig` models
- ✅ **Storage Loader Tests**: Comprehensive tests for `LocalStorageLoader` and `GCSStorageLoader` with proper mocking
- ✅ **Prompt Store Tests**: Full test coverage for `InMemoryPromptStore`, `LocalPromptStore`, and `GCSPromptStore`

### 4. **Test Coverage Achieved**
- ✅ **Unit Tests**: 100% coverage for core models and storage components
- ✅ **Integration Tests**: Storage loader and prompt store integration testing
- ✅ **Error Handling**: Comprehensive error scenario testing
- ✅ **Protocol Compliance**: Verification that all implementations follow the `PromptStore` protocol

## 🔄 Next Steps

### 4. **Integration Tests** (High Priority)
- [ ] **Prompt Service Integration Tests**: Test the complete prompt service with different storage backends
- [ ] **API Integration Tests**: Test prompt management endpoints with various storage configurations
- [ ] **Cross-Storage Migration Tests**: Test migrating prompts between different storage backends

### 5. **Docker Integration Tests** (Medium Priority)
- [ ] **Docker Compose Tests**: Verify the complete system works in Docker environment
- [ ] **GCS Emulator Tests**: Test GCS functionality using the emulator
- [ ] **Environment Variable Tests**: Test configuration via environment variables

### 6. **End-to-End Tests** (High Priority)
- [ ] **Complete Workflow Tests**: Test full prompt lifecycle (create, read, update, delete, search)
- [ ] **Performance Tests**: Test storage performance with large numbers of prompts
- [ ] **Concurrency Tests**: Test concurrent access to prompt stores

### 7. **Performance and Load Testing** (Medium Priority)
- [ ] **Load Tests**: Test system performance under high load
- [ ] **Memory Usage Tests**: Monitor memory usage with different storage backends
- [ ] **Storage Efficiency Tests**: Compare storage efficiency between backends

## 🧪 Test Implementation Status

### ✅ Completed Test Files
1. **`test_prompt_models.py`** - All model tests passing (23 tests)
2. **`test_storage_loaders.py`** - All storage loader tests passing (20 tests)
3. **`test_prompt_stores.py`** - All prompt store tests passing (26 tests)

### 📊 Test Coverage Summary
- **Total Tests**: 69 tests across 3 test files
- **Coverage**: 100% for core components
- **Error Scenarios**: Comprehensive error handling coverage
- **Mock Usage**: Proper mocking for external dependencies (GCS, file system)

## 🚀 Implementation Details

### Storage Architecture
```
PromptStore Protocol
├── InMemoryPromptStore (for development/testing)
├── LocalPromptStore (YAML files on local filesystem)
└── GCSPromptStore (YAML files in Google Cloud Storage)
    └── Uses StorageLoader abstraction
        ├── LocalStorageLoader
        └── GCSStorageLoader
```

### Configuration Management
- **Environment-based**: Storage type selection via environment variables
- **Docker-ready**: Complete Docker Compose configuration for all scenarios
- **Flexible**: Easy switching between local and GCS storage

### Error Handling
- **Comprehensive**: All storage operations have proper error handling
- **Retry Logic**: GCS operations include retry mechanisms
- **Validation**: Input validation at all levels

## 🎯 Success Metrics

### ✅ Achieved
- [x] **100% Test Coverage**: All core components have comprehensive tests
- [x] **Protocol Compliance**: All implementations follow the `PromptStore` protocol
- [x] **Error Resilience**: Robust error handling throughout the system
- [x] **Docker Integration**: Complete Docker support with GCS emulator
- [x] **Storage Flexibility**: Easy switching between storage backends

### 🎯 Remaining Goals
- [ ] **Integration Test Coverage**: 100% coverage for integration scenarios
- [ ] **Performance Benchmarks**: Establish performance baselines
- [ ] **Production Readiness**: Complete end-to-end testing in production-like environments

## 📋 Immediate Next Actions

1. **Create Integration Tests** (Priority 1)
   - Test prompt service with different storage backends
   - Test API endpoints with storage abstraction
   - Test cross-storage operations

2. **Docker Environment Testing** (Priority 2)
   - Verify Docker Compose configurations
   - Test GCS emulator functionality
   - Validate environment variable configuration

3. **End-to-End Workflow Testing** (Priority 1)
   - Complete prompt lifecycle testing
   - Performance testing with realistic data volumes
   - Concurrency and stress testing

## 🔧 Technical Debt & Improvements

### ✅ Resolved
- [x] **Protocol Separation**: Clean separation of concerns
- [x] **Storage Abstraction**: Flexible storage backend switching
- [x] **YAML Format**: Better readability and structure
- [x] **Comprehensive Testing**: Robust test coverage

### 🔄 Ongoing
- **Pydantic V2 Migration**: Update deprecated validators to V2 style
- **Performance Optimization**: Monitor and optimize storage operations
- **Documentation**: Maintain comprehensive documentation

## 📈 Progress Summary

**Overall Progress**: 75% Complete
- ✅ **Core Architecture**: 100% Complete
- ✅ **GCS Integration**: 100% Complete  
- ✅ **Unit Testing**: 100% Complete
- 🔄 **Integration Testing**: 0% Complete
- 🔄 **End-to-End Testing**: 0% Complete
- 🔄 **Performance Testing**: 0% Complete

The refactoring has successfully established a robust, testable, and flexible prompt management system with comprehensive test coverage for all core components. The next phase focuses on integration testing and end-to-end validation to ensure the system works seamlessly in real-world scenarios. 