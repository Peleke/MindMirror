from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"

    @strawberry.field
    def version(self) -> str:
        return "0.1.0"


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(graphql_app, prefix="/graphql")


