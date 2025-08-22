# Meals Microservice

A FastAPI-based microservice for managing meals, food items, nutrition tracking, and water consumption.

## Architecture

This service follows a layered architecture pattern:

```
meals/
├── repository/          # Data access layer
│   ├── models/         # SQLAlchemy models
│   └── repositories/   # Repository implementations
├── domain/             # Domain models (Pydantic)
├── service/            # Business logic layer
│   └── services/       # Service implementations
├── web/                # Web layer
│   └── graphql/        # GraphQL schema and resolvers
└── monitoring/         # Observability
```

## Data Models

### Core Entities

1. **FoodItem** - Base nutrition information for foods
   - Comprehensive nutrition data (macros, micros, vitamins, minerals)
   - Serving size and unit information
   - Created/modified timestamps

2. **Meal** - Collection of foods for a specific meal type and time
   - Meal type (breakfast, lunch, dinner, snack)
   - Date and time information
   - User association
   - Notes

3. **MealFood** - Junction table linking meals to food items
   - Quantity and serving unit
   - Links meals to food items with specific portions

4. **UserGoals** - Daily nutrition and water goals per user
   - Calorie, water, and macro goals
   - User-specific customization

5. **WaterConsumption** - Water intake tracking
   - Quantity and timestamp
   - User association

### Database Schema

All tables are created in the `meals` schema with the following structure:

- **food_items** - Food nutrition database
- **meals** - User meal records
- **meal_foods** - Many-to-many relationship between meals and foods
- **user_goals** - User-specific daily goals
- **water_consumption** - Water intake logs

## Current Implementation Status

### ✅ Completed
- [x] Project structure and configuration
- [x] SQLAlchemy models with relationships
- [x] Database configuration and session management
- [x] Unit of Work pattern for dependency injection
- [x] Domain models (Pydantic)
- [x] Repository implementations with full CRUD operations

### 🚧 In Progress
- [ ] Service layer
- [ ] GraphQL schema and resolvers
- [ ] FastAPI application setup

### 📋 TODO
- [ ] Database migrations (Alembic)
- [ ] Unit tests
- [ ] Integration tests
- [ ] API documentation
- [ ] Docker configuration
- [ ] Monitoring and logging setup

## Repository Layer

The repository layer follows the Unit of Work pattern and provides:

### Key Features
- **No Direct Commits**: Repositories use `flush()` for immediate ID access but rely on UoW for transaction management
- **Domain Model Returns**: All repositories return domain models using Pydantic validation
- **Complex Relationship Handling**: Proper loading of nested relationships (e.g., meals with food items)
- **Comprehensive CRUD**: Full create, read, update, delete operations for all entities

### Repository Implementations

1. **FoodItemRepository**: CRUD operations for food items with search capabilities
2. **MealRepository**: Complex meal management with nested food relationships
3. **UserGoalsRepository**: User goal management with upsert functionality 
4. **WaterConsumptionRepository**: Water tracking with date-based aggregations

### Usage Pattern
```python
async with uow:
    meal_repo = MealRepository(uow.session)
    meal = await meal_repo.get_meal_by_id(meal_id)
    # ... business logic ...
    await uow.commit()  # UoW handles transaction
```

## Development Setup

1. Install dependencies:
```bash
cd backend/meals
poetry install
```

2. Set environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_NAME=swae
```

3. Run database migrations (when available):
```bash
poetry run alembic upgrade head
```

4. Start the development server (when available):
```bash
poetry run start
```

## API Design

The service will expose a GraphQL API with the following capabilities:

### Queries
- Get meals for a specific date range
- Search food items
- Get user nutrition goals
- Get water consumption history
- Get nutrition summaries and analytics

### Mutations
- Create/update/delete meals
- Add/remove foods from meals
- Update user goals
- Log water consumption
- Bulk operations for meal planning

## Integration

This service integrates with:
- **Users Service** - User authentication and profiles (using internal user IDs)
- **Gateway** - API routing and federation
- **Frontend** - Flutter mobile application

## Data Migration

The service will replace the current Supabase-based implementation in the Flutter frontend, requiring:
- Data migration from Supabase to PostgreSQL
- API endpoint updates in the frontend
- GraphQL query/mutation replacements 

# Meals Service

## Migrations (Alembic)

Initialize (already added to repo):
- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/0001_init.py`

Run migrations locally:

```bash
poetry install
export DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST:5432/DB
poetry run alembic upgrade head
```

Create a new migration after model changes:

```bash
poetry run alembic revision --autogenerate -m "describe change"
poetry run alembic upgrade head
```

Cloud Run deploy will not run Alembic automatically; apply migrations via CI/CD step or manual run. 