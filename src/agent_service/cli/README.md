# Agent Service CLI

Command-line tools for managing agent service data and knowledge bases.

## Installation

```bash
# Install the CLI
pip install -e src/agent_service/cli/

# Or run directly
python -m agent_service.cli.main
```

## Commands

### Build Knowledge Base

Build knowledge bases from document sources:

```bash
# Build all traditions
agent-service build-knowledge-base

# Build specific tradition
agent-service build-knowledge-base --tradition canon-default

# Build from specific source directories
agent-service build-knowledge-base --source-dirs /path/to/docs1 /path/to/docs2

# Clear existing and rebuild
agent-service build-knowledge-base --clear-existing
```

### Health Check

Check the health of knowledge bases and services:

```bash
# Check all traditions
agent-service health-check

# Check specific tradition
agent-service health-check --tradition canon-default
```

### Clear Tradition

Clear a tradition's knowledge base:

```bash
# Clear with confirmation
agent-service clear-tradition --tradition canon-default

# Clear without confirmation
agent-service clear-tradition --tradition canon-default --confirm
```

### List Traditions

List available traditions and their document sources:

```bash
# List all traditions
agent-service list-traditions

# List from specific source directories
agent-service list-traditions --source-dirs /path/to/docs
```

## Examples

### Initial Setup

```bash
# 1. Check what traditions are available
agent-service list-traditions

# 2. Build knowledge base for all traditions
agent-service build-knowledge-base --clear-existing

# 3. Verify the build
agent-service health-check
```

### Rebuilding a Specific Tradition

```bash
# Clear and rebuild a specific tradition
agent-service build-knowledge-base --tradition canon-default --clear-existing

# Verify the tradition
agent-service health-check --tradition canon-default
```

### Troubleshooting

```bash
# Check if Qdrant is accessible
agent-service health-check

# Clear problematic tradition
agent-service clear-tradition --tradition canon-default --confirm

# Rebuild with verbose logging
agent-service build-knowledge-base --tradition canon-default --verbose
```

## Configuration

The CLI uses the same configuration as the main agent service:

- `DATA_DIR`: Base directory for data sources
- `QDRANT_URL`: Qdrant connection URL
- `CHUNK_SIZE`: Document chunking size
- `CHUNK_OVERLAP`: Document chunking overlap

## File Structure

Expected document structure:

```
data/
├── canon-default/
│   └── documents/
│       ├── document1.pdf
│       ├── document2.txt
│       └── ...
├── another-tradition/
│   └── documents/
│       ├── doc1.pdf
│       └── ...
```

## Error Handling

The CLI provides detailed error messages and progress indicators:

- ✅ Success operations
- ❌ Failed operations  
- ⚠️ Warnings
- 🔄 Progress indicators

Use `--verbose` flag for detailed logging information. 