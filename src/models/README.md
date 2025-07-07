# Central Models Aggregator

This module aggregates SQLAlchemy models from all MindMirror services into a single metadata object for use by Alembic and other tools.

## Purpose

The central models aggregator solves the problem of having multiple services with their own SQLAlchemy models that need to be managed together in a monorepo setup. It provides:

- **Single Source of Truth**: One metadata object containing all models
- **Service Independence**: Each service can define its own models
- **Conflict Resolution**: Handles table name conflicts across services
- **Easy Integration**: Simple import for Alembic and other tools

## Usage

### Basic Usage

```python
from src.models import metadata

# Use metadata for Alembic target_metadata
target_metadata = metadata
```

### Advanced Usage

```python
from src.models import metadata, load_all_models, get_loaded_services, get_table_names

# Reload all models
load_all_models()

# Check which services were loaded
services = get_loaded_services()
print(f"Loaded services: {services}")

# Get all table names
tables = get_table_names()
print(f"Available tables: {tables}")
```

## Architecture

### How It Works

1. **Import Detection**: The module automatically detects and imports models from available services
2. **Metadata Aggregation**: Tables from each service are copied into a single metadata object
3. **Conflict Handling**: Duplicate table names are logged as warnings
4. **Error Resilience**: Failed imports don't break the entire system

### Supported Services

- **journal_service**: Journal entries and related models
- **agent_service**: Agent and conversation models (if any)
- **shared**: Shared models across services (future)

### File Structure

```
src/models/
├── __init__.py          # Main aggregator module
└── README.md           # This documentation
```

## Integration with Alembic

The metadata object is designed to work seamlessly with Alembic:

```python
# In alembic/env.py
from src.models import metadata

target_metadata = metadata
```

## Error Handling

The module is designed to be resilient:

- **Missing Services**: Services that can't be imported are logged as warnings
- **Import Errors**: Individual service failures don't break the entire system
- **Table Conflicts**: Duplicate table names are logged but don't cause failures

## Development

### Adding a New Service

1. Create your service models with a `Base` class
2. The aggregator will automatically detect and load them
3. No changes needed to the aggregator code

### Debugging

Enable debug logging to see which tables are loaded:

```python
import logging
logging.getLogger('src.models').setLevel(logging.DEBUG)
```

### Testing

The module can be tested independently:

```python
from src.models import metadata, get_loaded_services

# Check if models were loaded
assert len(metadata.tables) > 0
assert 'journal_service' in get_loaded_services()
```

## Future Enhancements

- **Schema Support**: Better handling of different database schemas
- **Model Validation**: Validate model compatibility across services
- **Migration Helpers**: Utilities for managing cross-service migrations
- **Performance**: Optimize model loading for large numbers of tables 