"""
GraphQL Router Setup

Clean GraphQL router setup with proper schema composition and context management.
"""

import strawberry
from strawberry.fastapi import GraphQLRouter

from agent_service.app.graphql.context import GraphQLContext, get_context
from agent_service.app.graphql.schemas.mutation import Mutation
from agent_service.app.graphql.schemas.query import Query

# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)

# Create GraphQL router
graphql_app = GraphQLRouter(
    schema=schema,
    graphiql=True,  # Enable GraphiQL interface
    context_getter=get_context,
)
