from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Strawberry extensions if you plan to use them, e.g., for tracing
# from strawberry.extensions.tracing import ApolloTracingExtension, OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter

# Meals specific imports
from meals.repository.database import (  # Ensure these are in your database.py
    close_db,
    init_db,
)
from meals.repository.uow import UnitOfWork
from meals.web.config import Config
from meals.web.graphql.dependencies import get_uow  # Corrected import path
from meals.web.graphql.schema import get_schema  # Corrected import path

# from starlette.middleware.base import BaseHTTPMiddleware # If you add custom logging middleware



API_VERSION = Config.API_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database for meals service...")
    try:
        await init_db()  # This function needs to use Config.DATABASE_URL
    except Exception as exc:
        # Log and continue boot so Cloud Run can become healthy; endpoints that need DB will fail at use-time
        print(f"[WARN] init_db failed during startup: {exc}")
    yield
    print("Closing database connection for meals service...")
    try:
        await close_db()  # This function needs to manage the engine used by init_db
    except Exception as exc:
        print(f"[WARN] close_db failed during shutdown: {exc}")


async def get_context(uow: UnitOfWork = Depends(get_uow)):
    return {"uow": uow}


app = FastAPI(
    title="Meals API",
    description="API for managing meals, food items, and nutritional data",
    version=API_VERSION,
    lifespan=lifespan,
)

# app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware) # Example if you add logging

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define extensions if any (e.g., for logging, tracing)
graphql_extensions = [
    # LoguruStrawberryExtension(), # Example if you set up Loguru extension
    # OpenTelemetryExtension(), # Example if you set up OpenTelemetry
]

# Create schema with extensions (or without if none are used initially)
schema_with_extensions = get_schema(extensions=graphql_extensions if graphql_extensions else None)

graphql_app = GraphQLRouter(
    schema_with_extensions,
    graphiql=Config.DEBUG_GRAPHQL_SERVER,
    context_getter=get_context,
)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Meals backend is running. Visit /graphql for the GraphQL API."}
