# Users Service

A backend microservice responsible for user coordination across multiple services. This service manages users, links them to external services, and provides aggregated data to power user profile and home pages.

## Overview

The Users Service acts as a central coordination point for user management and cross-service data aggregation. Rather than duplicating data from other microservices, it serves as an orchestration layer that fetches and presents unified data views for user-focused features.

## Tech Stack

- **PostgreSQL (via Supabase)**: Database for user and relationship storage
- **FastAPI**: REST endpoints and orchestration logic
- **Strawberry**: GraphQL layer for typed, schema-first queries

## Database Design

The service uses Supabase as the backend database with the following schema:

### `users` Table

Stores core user information.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT now()
);
```

### `user_services` Junction Table

Defines many-to-many relationships between users and services.

```sql
CREATE TABLE user_services (
  user_id UUID REFERENCES users(id),
  service_id TEXT,
  PRIMARY KEY (user_id, service_id)
);
```

### `services` Table

Stores metadata about available services.

```sql
CREATE TABLE services (
  service_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

## Registered Services

The following external services are supported, each identified by a unique `service_id` and human-readable `name`:

| Service ID | Name | Description |
|------------|------|-------------|
| `meals` | Meals | Nutrition and meal planning service |
| `fitness` | Fitness | Workout and exercise tracking |
| `shadow_boxing` | Shadow Boxing | Boxing training and technique practice |
| `practices` | Practices | General practice and skill development |
| `programs` | Programs | Structured learning and training programs |

## Core Functionality

### Philosophy

This service **does not duplicate data** from other services. Instead, it acts as a coordinator and aggregator, focusing on:

- Cross-service orchestration
- User-focused data aggregation
- Unified presentation layers for UI components
- Authentication and identity isolation

### Key Endpoint

#### `GET /users/today`

Returns a list of the user's scheduled tasks for the day, grouped by service.

**Response Format:**
```json
{
  "user_id": "uuid",
  "date": "2024-01-15",
  "services": [
    {
      "service_id": "practices",
      "service_name": "Practices",
      "schedulables": [
        {
          "id": "practice-123",
          "title": "Morning Guitar Practice",
          "description": "30-minute scales and chord progressions",
          "service_id": "practices",
          "is_complete": false,
          "scheduled_time": "09:00",
          "estimated_duration": 30
        }
      ]
    },
    {
      "service_id": "fitness",
      "service_name": "Fitness",
      "schedulables": [
        {
          "id": "workout-456",
          "title": "Upper Body Strength",
          "description": "Chest, shoulders, and triceps workout",
          "service_id": "fitness",
          "is_complete": true,
          "scheduled_time": "06:00",
          "estimated_duration": 45
        }
      ]
    }
  ]
}
```

### The Schedulable Concept

A `Schedulable` is a **virtual entity** that doesn't exist as a database table in this service. Instead, it's generated through the following process:

1. **Fetch** an entity from a target service (e.g., `Practice` from practices service)
2. **Extract** ID and presentation data for UI rendering
3. **Transform** into a standardized format suitable for card display
4. **Present** in unified lists alongside other service types

#### Schedulable Properties

```typescript
interface Schedulable {
  id: string;                    // Source entity ID
  title: string;                 // Display name
  description: string;           // Brief description
  service_id: string;           // Originating service
  is_complete: boolean;         // Completion status
  scheduled_time?: string;      // When scheduled (HH:MM)
  estimated_duration?: number;  // Duration in minutes
  progress?: number;           // Progress percentage (0-100)
}
```

#### UI Interaction Flow

1. User sees Schedulable cards in a unified list
2. User clicks on a card
3. UI uses the `id` and `service_id` to route to the appropriate service
4. Target service provides detailed view/interaction

This design allows multiple entity types to coexist in a single, type-safe list while maintaining service boundaries.

## API Architecture

### REST Endpoints (FastAPI)

- `GET /users/today` - Daily task aggregation
- `GET /users/{user_id}/profile` - User profile data
- `POST /users/{user_id}/services` - Link user to service
- `DELETE /users/{user_id}/services/{service_id}` - Unlink user from service
- `GET /users/{user_id}/services` - List user's linked services

### GraphQL Layer (Strawberry)

Provides typed access to aggregated user data with support for:

- Nested queries across service boundaries
- Real-time subscriptions for user updates
- Efficient field selection and data fetching
- Type-safe Schedulable queries

#### Example GraphQL Query

```graphql
query UserToday($userId: UUID!, $date: Date!) {
  user(id: $userId) {
    id
    email
    todaySchedulables(date: $date) {
      serviceId
      serviceName
      items {
        id
        title
        description
        isComplete
        scheduledTime
        estimatedDuration
      }
    }
  }
}
```

## Service Responsibilities

### ✅ This Service IS Responsible For:

- **User Management**: Creating, updating, and maintaining user records
- **Service Linking**: Managing relationships between users and external services
- **Data Aggregation**: Fetching and combining data from multiple services
- **Authentication Coordination**: Centralizing auth logic across services
- **Unified APIs**: Providing consistent interfaces for user-focused features
- **Cross-Service Orchestration**: Coordinating workflows that span multiple services

### ❌ This Service IS NOT Responsible For:

- **Business Logic**: Domain-specific logic belongs in feature services
- **Data Storage**: Detailed entity storage (meals, workouts, etc.)
- **Direct Scheduling**: Scheduling logic lives in respective services
- **Progress Tracking**: Detailed progress/analytics remain in source services
- **Feature-Specific Operations**: Service-specific CRUD operations

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (or Supabase account)
- Docker (optional, for local development)

### Installation

```bash
# Clone and navigate to service
cd backend/users

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database and service URLs
```

### Running the Service

```bash
# Development server
uvicorn app.main:app --reload --port 8001

# With Docker
docker-compose up users-service
```

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@localhost/users_db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
PRACTICES_SERVICE_URL=http://localhost:8002
FITNESS_SERVICE_URL=http://localhost:8003
MEALS_SERVICE_URL=http://localhost:8004
# ... other service URLs
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Integration tests
pytest tests/integration/
```

## Architecture Decisions

### Why Virtual Schedulables?

1. **Service Autonomy**: Each service maintains ownership of its data
2. **Flexibility**: Easy to add new services without schema changes
3. **Performance**: Avoid data duplication and sync issues
4. **Consistency**: Unified presentation layer across diverse entity types

### Why Separate GraphQL + REST?

- **REST**: Simple, cacheable endpoints for standard operations
- **GraphQL**: Complex queries with precise field selection for UI needs
- **Flexibility**: Different clients can choose the most appropriate API style

## Contributing

1. Follow the established service patterns
2. Add comprehensive tests for new endpoints
3. Update this README for significant changes
4. Ensure cross-service compatibility when modifying Schedulable format

## Related Services

- **Practices Service**: `/backend/practices`
- **Fitness Service**: `/backend/fitness`
- **Meals Service**: `/backend/meals`
- **API Gateway**: `/backend/gateway`