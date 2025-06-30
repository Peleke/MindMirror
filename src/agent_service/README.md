# Agent Service

The AI Agent Service for MindMirror - a microservice that provides intelligent conversation and knowledge base management capabilities.

## Overview

The Agent Service is responsible for:
- Managing AI-powered conversations
- Building and querying knowledge bases
- Processing documents and traditions
- Providing GraphQL API endpoints for the frontend

## Features

- **Conversation Management**: Handle multi-turn conversations with AI agents
- **Knowledge Base Operations**: Build, query, and manage vector-based knowledge bases using Qdrant
- **Document Processing**: Process PDF and text documents for knowledge extraction
- **Tradition Management**: Organize knowledge by traditions (e.g., philosophical schools, domains)
- **GCS Integration**: Support for Google Cloud Storage with local emulator fallback
- **GraphQL API**: Modern GraphQL interface for frontend integration

## Architecture

The service follows a microservice architecture with:
- **FastAPI**: Modern async web framework
- **LangGraph**: AI agent orchestration
- **Qdrant**: Vector database for knowledge storage
- **PostgreSQL**: Relational data storage
- **Redis**: Caching and session management

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry for dependency management
- Docker (for containerized deployment)

### Local Development

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run the service:
   ```bash
   poetry run uvicorn agent_service.app.main:app --reload
   ```

### Docker Deployment

```bash
docker compose up agent_service
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_EMULATOR_HOST` | GCS emulator host | `gcs-emulator:4443` |
| `TRADITION_DISCOVERY_MODE` | Tradition discovery strategy | `gcs-first` |
| `PROMPT_STORAGE_TYPE` | Prompt storage backend | `yaml` |
| `GCS_BUCKET_NAME` | GCS bucket for traditions | `canon-default` |

## API Endpoints

- **Health Check**: `GET /health`
- **GraphQL**: `POST /graphql`
- **OpenAPI Docs**: `GET /docs`

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black .
poetry run isort .
```

### Linting

```bash
poetry run flake8
```

## Project Structure

```
agent_service/
├── app/                    # FastAPI application
│   ├── api/               # API routes and GraphQL
│   ├── models/            # Pydantic models
│   ├── repositories/      # Data access layer
│   └── services/          # Business logic
├── langgraph_/            # AI agent orchestration
├── llms/                  # LLM integrations
├── tests/                 # Test suite
└── pyproject.toml         # Dependencies and configuration
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

Part of the MindMirror project. 