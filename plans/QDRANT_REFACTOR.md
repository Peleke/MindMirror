# Qdrant & Embedding Architecture Refactoring Plan

## Current State Analysis

### Problem 1: Improper Qdrant Asset Usage

**Current Issues:**
- `qdrant_engine.py` is used directly in GraphQL queries (`app/graphql/schemas/query.py`)
- `qdrant_engine.py` imports from `agent_service.chain` and `agent_service.embedding`
- Direct embedding calls in GraphQL mutations and queries
- No proper layering - business logic mixed with data access

**Current Import Chain:**
```
GraphQL Query → qdrant_engine → chain → llm → embedding
```

**What Should Happen:**
```
GraphQL Query → LLMService → LangGraph → QdrantRetriever → QdrantClient
```

### Problem 2: Embedding Logic Scattered

**Current Issues:**
- `embedding.py` used directly in multiple places:
  - `app/graphql/schemas/mutation.py`
  - `app/graphql/schemas/query.py` 
  - `cli/qdrant_data_processing.py`
  - `qdrant_engine.py`
- No centralized embedding service
- Duplicate embedding logic across CLI and main service

### Problem 3: QdrantClient vs QdrantEngine Confusion

**Current State:**
- `QdrantClient` in `app/clients/qdrant_client.py` - HTTP client for celery-worker
- `QdrantEngine` in `qdrant_engine.py` - Direct Qdrant operations
- `QdrantKnowledgeBaseBuilder` in `cli/qdrant_data_processing.py` - CLI-specific builder
- Overlapping responsibilities and inconsistent interfaces

## Architectural Principles

1. **Separation of Concerns**: Data access, business logic, and presentation layers
2. **Dependency Inversion**: High-level modules shouldn't depend on low-level modules
3. **Single Responsibility**: Each module has one clear purpose
4. **Interface Segregation**: Clients shouldn't depend on interfaces they don't use
5. **Open/Closed**: Open for extension, closed for modification

## Proposed Architecture

### Layer 1: Data Access Layer
```
app/clients/
├── qdrant_client.py          # HTTP client for celery-worker communication
├── qdrant_retriever.py       # LangChain retriever for Qdrant
└── embedding_client.py       # HTTP client for embedding service
```

### Layer 2: Domain Services
```
app/services/
├── llm_service.py           # Main LLM orchestration (existing)
├── qdrant_service.py        # Qdrant operations abstraction
├── embedding_service.py     # Embedding operations abstraction
└── search_service.py        # Search orchestration
```

### Layer 3: Application Services
```
app/services/
├── chat_service.py          # Chat/ask operations
├── journal_service.py       # Journal operations
└── knowledge_service.py     # Knowledge base operations
```

### Layer 4: GraphQL Layer
```
app/graphql/
├── schemas/
│   ├── query.py            # Only calls application services
│   └── mutation.py         # Only calls application services
└── resolvers/              # Business logic resolvers
```

## Detailed Refactoring Plan

### Phase 1: Create Proper Service Layer

#### 1.1 Create QdrantService
**File:** `app/services/qdrant_service.py`

```python
class QdrantService:
    """High-level Qdrant operations service."""
    
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client
    
    async def search_knowledge_base(self, query: str, tradition: str, limit: int = 10):
        """Search knowledge base using Qdrant."""
        # Implementation using QdrantClient
    
    async def search_personal_entries(self, query: str, user_id: str, tradition: str, limit: int = 10):
        """Search personal journal entries."""
        # Implementation using QdrantClient
    
    async def hybrid_search(self, query: str, user_id: str, tradition: str, **kwargs):
        """Combined search across knowledge and personal data."""
        # Implementation using QdrantClient
```

#### 1.2 Create EmbeddingService
**File:** `app/services/embedding_service.py`

```python
class EmbeddingService:
    """Centralized embedding operations."""
    
    def __init__(self, embedding_client: EmbeddingClient):
        self.embedding_client = embedding_client
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text."""
        # Implementation using EmbeddingClient
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        # Implementation using EmbeddingClient
```

#### 1.3 Create SearchService
**File:** `app/services/search_service.py`

```python
class SearchService:
    """Orchestrates search operations across different data sources."""
    
    def __init__(self, qdrant_service: QdrantService, embedding_service: EmbeddingService):
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
    
    async def semantic_search(self, query: str, user_id: str, tradition: str, **kwargs):
        """Perform semantic search across all data sources."""
        # Get embedding
        # Perform search
        # Return results
```

### Phase 2: Create LangGraph Integration

#### 2.1 Create QdrantRetriever
**File:** `app/clients/qdrant_retriever.py`

```python
class QdrantRetriever(BaseRetriever):
    """LangChain retriever for Qdrant."""
    
    def __init__(self, qdrant_service: QdrantService, tradition: str):
        self.qdrant_service = qdrant_service
        self.tradition = tradition
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents from Qdrant."""
        # Implementation using QdrantService
```

#### 2.2 Create Chat Graph
**File:** `langgraph_/graphs/chat_graph.py`

```python
class ChatGraphBuilder(BaseGraphBuilder):
    """Graph for chat/ask operations."""
    
    def build(self) -> StateGraph:
        # Create RAG node with QdrantRetriever
        # Create response generation node
        # Connect nodes
        # Return compiled graph
```

#### 2.3 Update LLMService
**File:** `app/services/llm_service.py`

```python
class LLMService:
    """Enhanced LLM service with LangGraph integration."""
    
    async def ask(self, query: str, user_id: str, tradition: str) -> str:
        """Ask a question using LangGraph chat workflow."""
        # Create chat graph
        # Execute with query
        # Return response
```

### Phase 3: Refactor GraphQL Layer

#### 3.1 Update Query Schema
**File:** `app/graphql/schemas/query.py`

```python
# Remove direct imports of qdrant_engine and embedding
# Add imports for services
from agent_service.app.services.search_service import SearchService
from agent_service.app.services.llm_service import LLMService

class Query:
    def __init__(self, search_service: SearchService, llm_service: LLMService):
        self.search_service = search_service
        self.llm_service = llm_service
    
    @strawberry.field
    async def semantic_search(self, info: Info, query: str, tradition: str = "canon-default", **kwargs):
        """Semantic search using SearchService."""
        current_user = get_current_user_from_context(info)
        return await self.search_service.semantic_search(
            query=query,
            user_id=str(current_user.id),
            tradition=tradition,
            **kwargs
        )
    
    @strawberry.field
    async def ask(self, info: Info, query: str, tradition: str = "canon-default"):
        """Ask a question using LLMService."""
        current_user = get_current_user_from_context(info)
        return await self.llm_service.ask(
            query=query,
            user_id=str(current_user.id),
            tradition=tradition
        )
```

### Phase 4: CLI Refactoring

#### 4.1 Create CLI-Specific Services
**File:** `cli/services/qdrant_cli_service.py`

```python
class QdrantCLIService:
    """CLI-specific Qdrant operations."""
    
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client
    
    async def build_knowledge_base(self, tradition: str, source_dirs: List[Path]):
        """Build knowledge base for CLI operations."""
        # Implementation for CLI use
```

#### 4.2 Create CLI-Specific Embedding Service
**File:** `cli/services/embedding_cli_service.py`

```python
class EmbeddingCLIService:
    """CLI-specific embedding operations."""
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for CLI operations."""
        # Implementation for CLI use
```

#### 4.3 Update CLI Data Processing
**File:** `cli/qdrant_data_processing.py`

```python
# Update imports to use CLI services
from agent_service.cli.services.qdrant_cli_service import QdrantCLIService
from agent_service.cli.services.embedding_cli_service import EmbeddingCLIService

class QdrantKnowledgeBaseBuilder:
    def __init__(self, qdrant_service: QdrantCLIService, embedding_service: EmbeddingCLIService):
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
```

### Phase 5: Clean Up Legacy Code

#### 5.1 Remove Direct Dependencies
- Remove `from agent_service.qdrant_engine import get_qdrant_engine_for_tradition` from GraphQL
- Remove `from agent_service.embedding import get_embedding` from GraphQL
- Remove `from agent_service.chain import create_rag_chain` from qdrant_engine

#### 5.2 Deprecate Legacy Modules
- Mark `qdrant_engine.py` as deprecated
- Mark `embedding.py` as deprecated
- Mark `chain.py` as deprecated

#### 5.3 Update Tests
- Update all tests to use new service layer
- Create integration tests for new architecture
- Remove tests for deprecated modules

## Implementation Order

1. **Create service interfaces** (QdrantService, EmbeddingService, SearchService)
2. **Create CLI services** (QdrantCLIService, EmbeddingCLIService)
3. **Create LangGraph integration** (QdrantRetriever, ChatGraph)
4. **Update LLMService** to use LangGraph
5. **Refactor GraphQL layer** to use services
6. **Update CLI** to use CLI services
7. **Clean up legacy code**
8. **Update tests**

## Benefits

1. **Proper Layering**: Clear separation between data access, business logic, and presentation
2. **Testability**: Services can be easily mocked and tested
3. **Maintainability**: Changes in one layer don't affect others
4. **Reusability**: Services can be used by multiple consumers
5. **Consistency**: Uniform interfaces across the application
6. **Scalability**: Easy to add new features without breaking existing code

## Migration Strategy

1. **Parallel Implementation**: Implement new services alongside existing code
2. **Gradual Migration**: Move one GraphQL endpoint at a time
3. **Feature Flags**: Use feature flags to switch between old and new implementations
4. **Comprehensive Testing**: Ensure all functionality works before removing legacy code
5. **Documentation**: Update all documentation to reflect new architecture

## Success Criteria

- [ ] No direct imports of `qdrant_engine` or `embedding` in GraphQL layer
- [ ] All search operations go through `SearchService`
- [ ] All chat/ask operations go through `LLMService` with LangGraph
- [ ] CLI operations use CLI-specific services
- [ ] All tests pass with new architecture
- [ ] No deprecated modules in production code
- [ ] Clear separation between CLI and main service responsibilities 