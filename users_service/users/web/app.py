from contextlib import asynccontextmanager

import strawberry
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from users.repository.database import close_db, init_db
from users.repository.uow import UnitOfWork
from users.web.config import Config
from users.web.graphql.dependencies import (
    CurrentUser,
    get_current_user,
    get_request_uow,
    get_uow,
)
from users.web.graphql.schema import get_schema

API_VERSION = Config.API_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database for users service (non-blocking)...")
    try:
        # Fire-and-forget init so Cloud Run can pass startup probe even if DB is slow
        import asyncio

        asyncio.create_task(init_db())
    except Exception as exc:
        # Log and continue; endpoints that need DB will fail at request time
        print(f"DB init scheduling failed: {exc}")
    yield
    print("Closing database connection for users service...")
    await close_db()


app = FastAPI(
    title="Users API",
    description="API for managing users, roles, and associations.",
    version=API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define a function to build the context for Strawberry
async def get_context(
    request: Request,
    uow: UnitOfWork = Depends(get_uow),
    current_user_dep: CurrentUser = Depends(CurrentUser),
):
    current_user = await get_current_user(request=request, uow=uow, current_user_dep=current_user_dep)
    return {
        "request": request,
        "uow": uow,
        "current_user": current_user,
    }


# GraphQL Router Setup
# Define extensions (can be empty list if none are set up yet)
graphql_extensions = [
    # Example: LoguruStrawberryExtension(), # If you have it
    # Example: OpenTelemetryExtension(),   # If you have it
]

# Create schema with extensions
schema_with_extensions = get_schema(extensions=graphql_extensions)

graphql_app = GraphQLRouter(
    schema_with_extensions,  # Use the schema instance with extensions
    graphql_ide="graphiql" if Config.DEBUG_GRAPHQL_SERVER else None,
    context_getter=get_context,
)

# Mount at both paths to avoid 307 redirects for trailing slash
app.include_router(
    graphql_app,
    prefix="/graphql",
    dependencies=[Depends(get_request_uow)],  # This ensures UoW is created for every request
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "users", "version": API_VERSION}


@app.get("/sdl", include_in_schema=False, tags=["internal"])
async def get_schema_sdl():
    """
    Public SDL endpoint for schema composition.
    Returns GraphQL schema in SDL format.
    Used by mesh-compose to build supergraph.

    Note: Exposes schema structure only, not data.
    Data queries still require JWT authentication.
    """
    from fastapi.responses import Response
    return Response(
        content=str(schema_with_extensions),
        media_type="text/plain"
    )


@app.get("/")
async def root():
    return {"message": "Users service is running. Visit /graphql for the API."}
