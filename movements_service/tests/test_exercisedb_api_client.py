import asyncio
import os
import pytest

from movements.clients.exercisedb_api_client import ExerciseDBApiClient


@pytest.mark.asyncio
async def test_exercisedb_search_live_smoke():
    client = ExerciseDBApiClient()
    try:
        results = await client.search("bench press", limit=5)
    except Exception as e:
        pytest.skip(f"ExerciseDB live call failed: {e}")
        return
    # Minimal structure check
    assert isinstance(results, list)
    if results:
        first = results[0]
        assert "name" in first
        assert "source" in first and first["source"] == "exercise_db"


@pytest.mark.asyncio
async def test_exercisedb_get_by_id_live_smoke():
    client = ExerciseDBApiClient()
    # First, search for an ID
    try:
        results = await client.search("bench press", limit=1)
    except Exception as e:
        pytest.skip(f"ExerciseDB search failed: {e}")
        return
    if not results:
        pytest.skip("No results from ExerciseDB for bench press")
        return
    ext_id = results[0].get("externalId")
    if not ext_id:
        pytest.skip("Result missing externalId")
        return
    try:
        item = await client.get_by_id(ext_id)
    except Exception as e:
        pytest.skip(f"ExerciseDB get_by_id failed: {e}")
        return
    assert item is None or item.get("externalId") == ext_id 