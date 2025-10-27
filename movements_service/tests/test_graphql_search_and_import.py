import asyncio
import os
import pytest

from movements.web.schema import get_schema
from movements.repository.database import get_session_factory, Base
from movements.repository.movements_repo import MovementsRepoPg
from sqlalchemy import text


@pytest.mark.asyncio
async def test_graphql_search_and_import_live_api():
    # Ensure DB schema
    session_factory = get_session_factory()
    async with session_factory() as s:
        await s.execute(text('CREATE SCHEMA IF NOT EXISTS "movements"'))
        await s.commit()
    async with session_factory().bind.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as s:
        repo = MovementsRepoPg(s)
        schema = get_schema()

        # Query searchMovements
        query = """
        query Q($term: String) {
          searchMovements(searchTerm: $term, limit: 5) { name isExternal externalId }
        }
        """
        result = await schema.execute(query, variable_values={"term": "bench"}, context_value={"movements_repo": repo})
        assert not result.errors
        data = result.data["searchMovements"]
        assert isinstance(data, list)
        # If any external results, try import one
        external = next((r for r in data if r.get("isExternal") and r.get("externalId")), None)
        if external:
            ext_id = external["externalId"]
            mutation = """
            mutation M($id: String!) {
              importExternalMovement(externalId: $id) { id_ name }
            }
            """
            result2 = await schema.execute(mutation, variable_values={"id": ext_id}, context_value={"movements_repo": repo})
            assert not result2.errors
            assert result2.data["importExternalMovement"]["id_"] 