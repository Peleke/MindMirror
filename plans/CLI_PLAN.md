# CLI Decoupling and Typer Migration Plan

## Overview

This plan outlines the migration of CLI tools from `agent_service/cli/` to a top-level `cli/` directory with a Typer-based interface, complete decoupling from `agent_service`, and integration with the existing `make demo` workflow.

## Current State Analysis

### Current CLI Structure
```
src/agent_service/cli/
├── data_management.py      # Click-based CLI (unused)
├── qdrant_data_processing.py  # Core Qdrant builder logic
├── embedding.py            # Embedding utilities
└── main.py                 # CLI entry point (unused)
```

### Current Script
```
scripts/build_qdrant_knowledge_base.py  # Main script in use
```

### Dependencies to Decouple
- `agent_service.app.clients.qdrant_client.QdrantClient`
- `agent_service.cli.embedding.get_embedding`
- `agent_service.cli.qdrant_data_processing.QdrantKnowledgeBaseBuilder`

## Target Architecture

```
cli/
├── pyproject.toml          # Poetry project configuration
├── README.md              # CLI documentation
├── src/
│   └── mindmirror_cli/
│       ├── __init__.py
│       ├── main.py        # Typer app entry point
│       ├── commands/
│       │   ├── __init__.py
│       │   └── qdrant.py  # Qdrant subcommand
│       ├── core/
│       │   ├── __init__.py
│       │   ├── client.py  # QdrantClient clone
│       │   ├── builder.py # QdrantKnowledgeBaseBuilder clone
│       │   └── embedding.py # Embedding utilities clone
│       └── utils/
│           ├── __init__.py
│           ├── config.py  # Configuration management
│           └── progress.py # Progress reporting
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_commands/
│   │   └── test_qdrant.py
│   └── test_core/
│       ├── test_client.py
│       ├── test_builder.py
│       └── test_embedding.py
```

## Implementation Plan

### Phase 1: Create Top-Level CLI Project Structure

1. **Create `cli/` directory structure**
   ```bash
   mkdir -p cli/src/mindmirror_cli/{commands,core,utils}
   mkdir -p cli/tests/{test_commands,test_core}
   ```

2. **Create `pyproject.toml`**
   ```toml
   [tool.poetry]
   name = "mindmirror-cli"
   version = "0.1.0"
   description = "CLI tools for MindMirror knowledge base management"
   authors = ["Your Name <your.email@example.com>"]
   readme = "README.md"
   packages = [{include = "mindmirror_cli", from = "src"}]

   [tool.poetry.dependencies]
   python = "^3.9"
   typer = {extras = ["all"], version = "^0.9.0"}
   rich = "^13.0.0"
   qdrant-client = "^1.7.0"
   langchain = "^0.1.0"
   langchain-community = "^0.0.20"
   langchain-openai = "^0.0.5"
   langchain-ollama = "^0.1.0"
   click = "^8.1.0"

   [tool.poetry.group.dev.dependencies]
   pytest = "^7.0.0"
   pytest-asyncio = "^0.21.0"
   pytest-mock = "^3.10.0"
   black = "^23.0.0"
   isort = "^5.12.0"
   mypy = "^1.0.0"

   [tool.poetry.scripts]
   mindmirror = "mindmirror_cli.main:app"

   [build-system]
   requires = ["poetry-core"]
   build-backend = "poetry.core.masonry.api"
   ```

### Phase 2: Clone Core Dependencies

1. **Clone QdrantClient** (`cli/src/mindmirror_cli/core/client.py`)
   - Copy `agent_service.app.clients.qdrant_client.QdrantClient`
   - Remove any `agent_service` dependencies
   - Add configuration management for Qdrant URL, API key, etc.

2. **Clone Embedding Utilities** (`cli/src/mindmirror_cli/core/embedding.py`)
   - Copy `agent_service.cli.embedding.get_embedding`
   - Add configuration management for embedding providers
   - Support environment variables for API keys

3. **Clone QdrantKnowledgeBaseBuilder** (`cli/src/mindmirror_cli/core/builder.py`)
   - Copy `agent_service.cli.qdrant_data_processing.QdrantKnowledgeBaseBuilder`
   - Update imports to use local core modules
   - Add configuration management

### Phase 3: Create Typer Commands

1. **Main App** (`cli/src/mindmirror_cli/main.py`)
   ```python
   import typer
   from mindmirror_cli.commands import qdrant

   app = typer.Typer(
       name="mindmirror",
       help="MindMirror knowledge base management CLI",
       add_completion=False,
   )

   app.add_typer(qdrant.app, name="qdrant")

   if __name__ == "__main__":
       app()
   ```

2. **Qdrant Subcommand** (`cli/src/mindmirror_cli/commands/qdrant.py`)
   ```python
   import typer
   from typing import List, Optional
   from mindmirror_cli.core.builder import QdrantKnowledgeBaseBuilder

   app = typer.Typer(name="qdrant", help="Qdrant knowledge base operations")

   @app.command()
   def build(
       tradition: Optional[str] = typer.Option(None, "--tradition", "-t"),
       source_dirs: List[str] = typer.Option(["local_gcs_bucket", "pdfs"], "--source-dirs", "-s"),
       clear_existing: bool = typer.Option(False, "--clear-existing"),
       verbose: bool = typer.Option(False, "--verbose", "-v"),
   ):
       """Build knowledge base from documents."""
       # Implementation here

   @app.command()
   def health():
       """Check Qdrant service health."""
       # Implementation here

   @app.command()
   def list_traditions(source_dirs: List[str] = typer.Option(["local_gcs_bucket", "pdfs"], "--source-dirs", "-s")):
       """List available traditions."""
       # Implementation here

   @app.command()
   def list_collections():
       """List Qdrant collections."""
       # Implementation here
   ```

### Phase 4: Configuration Management

1. **Configuration System** (`cli/src/mindmirror_cli/utils/config.py`)
   ```python
   import os
   from typing import Optional
   from dataclasses import dataclass

   @dataclass
   class QdrantConfig:
       url: str = "http://localhost:6333"
       api_key: Optional[str] = None
       timeout: int = 30

   @dataclass
   class EmbeddingConfig:
       provider: str = "openai"  # or "ollama"
       model: str = "text-embedding-ada-002"
       api_key: Optional[str] = None
       base_url: Optional[str] = None

   def load_config() -> tuple[QdrantConfig, EmbeddingConfig]:
       # Load from environment variables and config files
   ```

### Phase 5: High DX Typer API Design

#### Command Structure
```bash
# Main commands
mindmirror qdrant build [OPTIONS]
mindmirror qdrant health [OPTIONS]
mindmirror qdrant list-traditions [OPTIONS]
mindmirror qdrant list-collections [OPTIONS]

# Build options
mindmirror qdrant build --tradition canon-default --clear-existing --verbose
mindmirror qdrant build --source-dirs ./docs ./pdfs --tradition canon-default

# Health checks
mindmirror qdrant health --detailed

# List resources
mindmirror qdrant list-traditions --source-dirs ./docs
mindmirror qdrant list-collections --verbose
```

#### Rich Output
- Progress bars for long-running operations
- Color-coded status indicators
- Tables for structured data
- JSON output option for scripting

#### Error Handling
- Graceful error messages with suggestions
- Exit codes for scripting
- Verbose mode for debugging

### Phase 6: Testing Strategy

1. **Unit Tests**
   - Test each core module independently
   - Mock external dependencies (Qdrant, embedding APIs)
   - Test configuration loading

2. **Integration Tests**
   - Test command execution with mocked services
   - Test error scenarios
   - Test CLI argument parsing

3. **Test Structure**
   ```
   tests/
   ├── conftest.py          # Pytest fixtures
   ├── test_commands/       # Command tests
   └── test_core/          # Core module tests
   ```

### Phase 7: Makefile Integration

1. **Update existing `Makefile`**
   ```makefile
   # Build knowledge base
   build-knowledge-base:
       @echo "🧠 Building Qdrant knowledge base..."
       @if [ -f cli/pyproject.toml ]; then \
           echo "📚 Running MindMirror CLI..."; \
           cd cli && poetry run mindmirror qdrant build --tradition canon-default --verbose || echo "⚠️  Knowledge base build failed or skipped"; \
       else \
           echo "⚠️  MindMirror CLI not found, falling back to script..."; \
           poetry run python scripts/build_qdrant_knowledge_base.py || echo "⚠️  Knowledge base build failed or skipped"; \
       fi
       @echo "✅ Knowledge base build complete!"
   ```

2. **CLI Installation in Makefile**
   ```makefile
   demo:
       @echo "🚀 Launching MindMirror Demo Environment..."
       # ... existing setup ...
       @echo "📁 Creating necessary directories..."
       @mkdir -p prompts credentials local_gcs_bucket
       @echo "🔧 Installing MindMirror CLI..."
       @if [ -f cli/pyproject.toml ]; then \
           cd cli && poetry install; \
       fi
       @echo "🧠 Building knowledge base..."
       @make build-knowledge-base
       # ... rest of demo setup ...
   ```

### Phase 8: Migration Steps

1. **Create new CLI project**
   ```bash
   mkdir cli
   cd cli
   poetry init
   # Add dependencies and structure
   ```

2. **Clone and adapt core modules**
   - Copy QdrantClient, adapt for standalone use
   - Copy embedding utilities, add configuration
   - Copy builder logic, update imports

3. **Create Typer commands**
   - Implement main app structure
   - Create qdrant subcommand module
   - Add rich output and error handling

4. **Add tests**
   - Unit tests for core modules
   - Integration tests for commands
   - Mock external dependencies

5. **Update Makefile**
   - Modify existing `build-knowledge-base` target
   - Add CLI installation to `demo` target
   - Test integration

6. **Documentation**
   - CLI usage examples
   - Configuration guide
   - Integration instructions

## Benefits

1. **Complete Decoupling**: No dependency on `agent_service`
2. **Modern CLI**: Typer provides better UX than Click
3. **Easy Integration**: Simple to call from existing `make demo`
4. **Extensible**: Easy to add new subcommands (not just qdrant)
5. **Testable**: Proper test structure
6. **Configurable**: Environment-based configuration
7. **Rich Output**: Better user experience with Rich
8. **Consistent Naming**: `mindmirror` as main tool, `qdrant` as subcommand

## Future Enhancements

1. **Additional Subcommands**: `mindmirror journal`, `mindmirror agent`, etc.
2. **Admin Panel**: Web UI for knowledge base management
3. **Additional Commands**: Backup, restore, migration tools
4. **Plugin System**: Extensible command architecture
5. **Configuration UI**: Interactive configuration setup
6. **Monitoring**: Health monitoring and alerting

## Timeline

- **Phase 1-2**: 30 minutes (Project setup and core module cloning)
- **Phase 3-4**: 15 minutes (Typer commands and configuration)
- **Phase 5-6**: 10 minutes (Testing and DX improvements)
- **Phase 7-8**: 5 minutes (Makefile integration and migration)

**Total**: ~1 hour for complete implementation 