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

### Phase 1: Foundation & Infrastructure (Week 1) ✅ **IN PROGRESS**

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

#### 🔄 In Progress
- [ ] **LLM Factory Tests**
  - `src/agent_service/tests/test_llm_factory.py`
- [ ] **Prompt Template Externalization**
  - `src/agent_service/llms/prompts/` directory
  - Jinja2 template files

#### 📋 Next Steps
1. **Complete LLM Factory Testing**
2. **Externalize All Prompts**
3. **Create Retriever Factory**
4. **Build Journal Processing Nodes**

---

### Phase 2: Modular Chain Architecture (Week 2)

#### 🎯 Objectives
- Refactor existing RAG chains into modular components
- Create journal processing chains
- Implement tool registry with GraphQL introspection

#### 📋 Tasks

##### 2.1 RAG Chain Refactoring
- [ ] **Test**: `test_rag_chain.py` - Test modular RAG chain components
- [ ] **Implementation**: `src/agent_service/chains/rag_chain.py` - Pure RAG chain
- [ ] **Test**: `test_retriever_factory.py` - Test retriever composition
- [ ] **Implementation**: `src/agent_service/retrievers/factory.py` - Retriever factory

##### 2.2 Journal Processing Chains
- [ ] **Test**: `test_journal_summary_chain.py` - Test journal summarization
- [ ] **Implementation**: `src/agent_service/chains/journal_summary_chain.py`
- [ ] **Test**: `test_performance_review_chain.py` - Test performance review generation
- [ ] **Implementation**: `src/agent_service/chains/performance_review_chain.py`

##### 2.3 Tool Registry & Introspection
- [ ] **Test**: `test_tool_registry.py` - Test tool registration and discovery
- [ ] **Implementation**: `src/agent_service/tools/registry.py` - Tool registry
- [ ] **Test**: `test_tool_schema.py` - Test GraphQL schema generation from tools
- [ ] **Implementation**: `src/agent_service/tools/schema.py` - GraphQL schema generation

#### 🏗️ Architecture Changes
```python
# Before: Monolithic engine
engine = CoachingEngine(tradition="canon-default")
response = engine.ask("What is my purpose?")

# After: Modular chains
rag_chain = RAGChain(retriever=qdrant_retriever)
summary_chain = JournalSummaryChain(llm=coaching_llm)
response = rag_chain.invoke({"query": "What is my purpose?"})
```

---

### Phase 3: LangGraph Agent Implementation (Week 3)

#### 🎯 Objectives
- Build LangGraph-based agents with state management
- Create agent orchestration layer
- Implement agent service interface

#### 📋 Tasks

##### 3.1 Core Agent Nodes
- [ ] **Test**: `test_agent_nodes.py` - Test individual agent nodes
- [ ] **Implementation**: `src/agent_service/agents/nodes/`
  - `summarize_node.py` - Journal summarization node
  - `review_node.py` - Performance review node
  - `router_node.py` - Intent routing node

##### 3.2 Agent Graphs
- [ ] **Test**: `test_coach_agent.py` - Test complete coach agent graph
- [ ] **Implementation**: `src/agent_service/agents/coach_agent.py` - Main coach agent
- [ ] **Test**: `test_agent_workflows.py` - Test different workflow patterns
- [ ] **Implementation**: `src/agent_service/agents/workflows.py` - Workflow definitions

##### 3.3 Agent Service Layer
- [ ] **Test**: `test_agent_service.py` - Test agent service interface
- [ ] **Implementation**: `src/agent_service/services/agent_service.py` - Agent orchestration
- [ ] **Test**: `test_agent_cache.py` - Test agent instance caching
- [ ] **Implementation**: `src/agent_service/services/agent_cache.py` - Agent caching

#### 🏗️ Architecture Changes
```python
# Before: Direct service calls
llm_service = LLMService()
summary = await llm_service.get_journal_summary(entries)

# After: LangGraph workflow
coach_agent = CoachAgent()
state = AgentStateFactory.create_journal_state(user_id, tradition, entries)
result = await coach_agent.ainvoke(state)
summary = result["summary"]
```

---

### Phase 4: Service Decomposition (Week 4)

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

#### 🏗️ Architecture Changes
```python
# Before: Monolithic service
suggestion_service = SuggestionService(engine, clients...)
meal = await suggestion_service.get_meal_suggestion(user, tradition, "breakfast")

# After: Modular services
coaching_service = CoachingService()
knowledge_service = KnowledgeService()
meal = await coaching_service.get_meal_suggestion(user, tradition, "breakfast")
```

---

### Phase 5: Memgraph Integration & Multi-Agent (Week 5)

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

#### 🏗️ Architecture Changes
```python
# Before: Single agent approach
engine = QdrantCoachingEngine(tradition="canon-default")
response = engine.ask("What should I eat?")

# After: Multi-agent orchestration
orchestrator = AgentOrchestrator()
workflow = orchestrator.create_workflow([
    "nutrition_agent",
    "coaching_agent", 
    "knowledge_agent"
])
result = await workflow.execute(user_query)
```

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
- **Response Time**: <2s for RAG queries
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

### Week 1: Foundation ✅ **IN PROGRESS**
- [x] LangSmith tracing infrastructure
- [x] State management system
- [x] First LangGraph node (RAG)
- [ ] LLM factory completion
- [ ] Prompt externalization

### Week 2: Modular Chains
- [ ] RAG chain refactoring
- [ ] Journal processing chains
- [ ] Tool registry implementation
- [ ] Retriever factory

### Week 3: LangGraph Agents
- [ ] Core agent nodes
- [ ] Agent graphs
- [ ] Agent service layer
- [ ] Workflow orchestration

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

### This Week (Phase 1 Completion)
1. **Complete LLM Factory Tests**
   ```bash
   pytest src/agent_service/tests/test_llm_factory.py -v
   ```

2. **Externalize Prompts**
   ```bash
   mkdir -p src/agent_service/llms/prompts
   # Create Jinja2 templates for all prompts
   ```

3. **Create Retriever Factory**
   ```bash
   # Implement retriever composition and factory pattern
   ```

4. **Build Journal Summary Node**
   ```bash
   # Create LangGraph node for journal summarization
   ```

### Next Week (Phase 2 Start)
1. **RAG Chain Refactoring**
2. **Journal Processing Chains**
3. **Tool Registry Implementation**

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