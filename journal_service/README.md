# Journal Service

A microservice for managing journal entries and reflections in the MindMirror platform. This service handles structured journaling with support for gratitude, reflection, and freeform entries.

## Overview

The Journal Service provides:
- **Structured Journaling**: Support for gratitude, reflection, and freeform journal entries
- **GraphQL API**: Modern GraphQL interface for client applications
- **Real-time Indexing**: Automatic indexing of entries for search and analysis
- **User Isolation**: Secure multi-tenant architecture
- **Scalable Architecture**: Built with FastAPI and SQLAlchemy for high performance

## Architecture

```
journal_service/
├── app/
│   ├── api/           # REST API endpoints
│   ├── db/            # Database models and repositories
│   ├── graphql/       # GraphQL schemas and resolvers
│   ├── services/      # Business logic layer
│   ├── clients/       # External service communication
│   └── models/        # Domain models and DTOs
├── tests/             # Test suite
└── alembic/           # Database migrations
```

### Key Components

- **Repository Pattern**: Clean data access layer with SQLAlchemy
- **Service Layer**: Business logic encapsulation
- **GraphQL Schema**: Type-safe API with Strawberry GraphQL
- **Task Integration**: Celery integration for background processing
- **Authentication**: JWT-based authentication with role-based access

## Features

### Journal Entry Types

1. **Gratitude Entries**
   - What you're grateful for
   - Impact on your life
   - Optional reflection

2. **Reflection Entries**
   - Prompt-based responses
   - Personal insights
   - Growth tracking

3. **Freeform Entries**
   - Unstructured content
   - General thoughts and feelings
   - Flexible format

### API Capabilities

- Create, read, and delete journal entries
- Check for daily entry completion
- Automatic indexing for search
- User-specific data isolation
- Real-time updates

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Poetry (for dependency management)

### Local Development

1. **Install dependencies**
   ```bash
   cd src/journal_service
   poetry install
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

4. **Start the service**
   ```bash
   poetry run uvicorn journal_service.main:app --reload --port 8001
   ```

### Docker Development

```bash
# From project root
docker compose up journal_service
```

## API Reference

### GraphQL Endpoint

- **URL**: `http://localhost:8001/graphql`
- **Playground**: Available at the same URL

### Key Queries

```graphql
# Get all journal entries for user
query {
  journalEntries {
    id
    entryType
    createdAt
    payload
  }
}

# Check if user has entry today
query {
  journalEntryExistsToday(entryType: "GRATITUDE")
}
```

### Key Mutations

```graphql
# Create gratitude entry
mutation {
  createGratitudeJournalEntry(input: {
    gratefulFor: "My supportive family"
    impact: "Provides emotional stability"
    reflection: "I feel more grounded"
  }) {
    id
    entryType
    payload {
      gratefulFor
      impact
    }
  }
}

# Create freeform entry
mutation {
  createFreeformJournalEntry(input: {
    content: "Today was challenging but productive..."
  }) {
    id
    entryType
    payload
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@postgres:5432/cyborg_coach` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `JWT_SECRET` | JWT signing secret | `your-secret-key` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |

### Database Schema

```sql
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    entry_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_journal_entries_user_id ON journal_entries(user_id);
CREATE INDEX idx_journal_entries_created_at ON journal_entries(created_at);
```

## Development

### Project Structure

```
journal_service/
├── app/
│   ├── api/                    # REST API endpoints
│   │   ├── health.py          # Health check endpoints
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── db/                    # Database layer
│   │   ├── database.py        # Connection setup
│   │   ├── models/            # SQLAlchemy models
│   │   └── repositories/      # Data access layer
│   ├── graphql/               # GraphQL layer
│   │   ├── context.py         # Context management
│   │   ├── schemas/           # Query/Mutation resolvers
│   │   └── types/             # GraphQL type definitions
│   ├── services/              # Business logic
│   │   ├── journal_service.py # Core journal logic
│   │   └── task_service.py    # Background task coordination
│   ├── clients/               # External service clients
│   │   └── task_client.py     # Celery worker communication
│   └── models/                # Domain models
│       ├── domain.py          # Core domain objects
│       ├── requests.py        # Request DTOs
│       └── responses.py       # Response DTOs
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data
└── alembic/                   # Database migrations
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=journal_service

# Run specific test categories
poetry run pytest tests/unit/
poetry run pytest tests/integration/
```

### Code Quality

```bash
# Format code
poetry run black journal_service/
poetry run isort journal_service/

# Type checking
poetry run mypy journal_service/

# Linting
poetry run ruff check journal_service/
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy application code
COPY journal_service/ ./journal_service/

# Run the application
CMD ["uvicorn", "journal_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: journal-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: journal-service
  template:
    metadata:
      labels:
        app: journal-service
    spec:
      containers:
      - name: journal-service
        image: mindmirror/journal-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## Monitoring & Observability

### Health Checks

- **Endpoint**: `GET /health`
- **Response**: Service status and dependencies

### Metrics

- Request count and latency
- Database connection pool status
- Celery task queue metrics
- Error rates and types

### Logging

Structured logging with correlation IDs for request tracing.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines

- Follow TDD (Test-Driven Development)
- Maintain >90% test coverage
- Use type hints throughout
- Follow PEP 8 style guidelines
- Write comprehensive docstrings

## License

This project is part of the MindMirror platform and follows the same licensing terms. 