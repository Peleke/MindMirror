# MindMirror CLI

A modern command-line interface for managing MindMirror knowledge bases and Qdrant vector stores.

## Features

- 🚀 **Fast Knowledge Base Building** - Build vector embeddings from PDF and text documents
- 🔍 **Health Monitoring** - Check Qdrant service health and collection status
- 📋 **Tradition Management** - List and manage different knowledge traditions
- 🎨 **Rich Output** - Beautiful tables and progress indicators with Rich
- ⚙️ **Flexible Configuration** - Environment-based configuration for different setups

## Installation

```bash
# Install dependencies
cd cli
poetry install

# Install the CLI globally (optional)
poetry install --with dev
```

## Quick Start

```bash
# Check if everything is working
mindmirror qdrant health

# List available traditions
mindmirror qdrant list-traditions

# Build knowledge base for a specific tradition
mindmirror qdrant build --tradition canon-default --verbose

# Build all traditions
mindmirror qdrant build --verbose
```

## Commands

### `mindmirror qdrant build`

Build knowledge base from documents.

```bash
# Build specific tradition
mindmirror qdrant build --tradition canon-default

# Build with custom source directories
mindmirror qdrant build --source-dirs ./docs ./pdfs --tradition canon-default

# Clear existing data before building
mindmirror qdrant build --tradition canon-default --clear-existing

# Verbose output
mindmirror qdrant build --tradition canon-default --verbose
```

**Options:**
- `--tradition, -t`: Specific tradition to build (default: all)
- `--source-dirs, -s`: Source directories to scan (default: local_gcs_bucket, pdfs)
- `--clear-existing`: Clear existing knowledge base before building
- `--verbose, -v`: Enable verbose output

### `mindmirror qdrant health`

Check Qdrant service health and collection status.

```bash
# Basic health check
mindmirror qdrant health
```

### `mindmirror qdrant list-traditions`

List available traditions and their document sources.

```bash
# List all traditions
mindmirror qdrant list-traditions

# List with custom source directories
mindmirror qdrant list-traditions --source-dirs ./docs
```

**Options:**
- `--source-dirs, -s`: Source directories to scan (default: local_gcs_bucket, pdfs)

### `mindmirror qdrant list-collections`

List Qdrant collections and their statistics.

```bash
# List all collections
mindmirror qdrant list-collections
```

## Configuration

The CLI uses environment variables for configuration:

### Qdrant Configuration

```bash
# Qdrant server URL
export QDRANT_URL="http://localhost:6333"

# Qdrant API key (if using cloud)
export QDRANT_API_KEY="your-api-key"
```

### Embedding Configuration

```bash
# Embedding provider (openai or ollama)
export EMBEDDING_PROVIDER="openai"

# OpenAI configuration
export OPENAI_API_KEY="your-openai-api-key"

# Ollama configuration
export OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
export OLLAMA_BASE_URL="http://localhost:11434"
```

### Document Processing Configuration

```bash
# Chunk size for document splitting
export CHUNK_SIZE="1000"

# Chunk overlap for document splitting
export CHUNK_OVERLAP="200"
```

## Directory Structure

The CLI expects documents to be organized in one of these structures:

### Modern Structure (Recommended)
```
local_gcs_bucket/
├── canon-default/
│   └── documents/
│       ├── document1.pdf
│       └── document2.txt
└── another-tradition/
    └── documents/
        └── document3.pdf
```

### Legacy Structure
```
pdfs/
├── canon-default/
│   ├── document1.pdf
│   └── document2.txt
└── another-tradition/
    └── document3.pdf
```

## Integration with Make Demo

The CLI integrates seamlessly with the `make demo` workflow:

```makefile
# In your Makefile
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

## Development

### Running Tests

```bash
cd cli
poetry run pytest
```

### Code Formatting

```bash
cd cli
poetry run black src/
poetry run isort src/
```

### Type Checking

```bash
cd cli
poetry run mypy src/
```

## Troubleshooting

### Qdrant Connection Issues

1. **Check if Qdrant is running:**
   ```bash
   mindmirror qdrant health
   ```

2. **Verify Qdrant URL:**
   ```bash
   export QDRANT_URL="http://localhost:6333"
   mindmirror qdrant health
   ```

### Embedding Issues

1. **Check API keys:**
   ```bash
   # For OpenAI
   export OPENAI_API_KEY="your-key"
   
   # For Ollama
   export EMBEDDING_PROVIDER="ollama"
   export OLLAMA_BASE_URL="http://localhost:11434"
   ```

2. **Test embedding generation:**
   ```bash
   mindmirror qdrant build --tradition test --verbose
   ```

### Document Processing Issues

1. **Check directory structure:**
   ```bash
   mindmirror qdrant list-traditions --source-dirs ./your-docs
   ```

2. **Verify file formats:**
   - Supported: `.pdf`, `.txt`
   - Ensure files are readable and not corrupted

## Examples

### Complete Workflow

```bash
# 1. Check health
mindmirror qdrant health

# 2. List available traditions
mindmirror qdrant list-traditions

# 3. Build knowledge base
mindmirror qdrant build --tradition canon-default --verbose

# 4. Verify collections
mindmirror qdrant list-collections
```

### Batch Processing

```bash
# Build multiple traditions
mindmirror qdrant build --source-dirs ./docs1 ./docs2 --verbose

# Clear and rebuild
mindmirror qdrant build --tradition canon-default --clear-existing --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is part of MindMirror and follows the same license terms. 