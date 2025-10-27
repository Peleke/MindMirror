import asyncio
import os
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from practices.repository.models.practice_template import MovementTemplateModel

MOVEMENTS_GRAPHQL_URL = os.getenv("MOVEMENTS_GRAPHQL_URL", "http://localhost:8052/graphql")
DATABASE_URL = os.getenv("PRACTICES_DB_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/practices")

SEARCH_QUERY = """
query Search($term: String!, $limit: Int) {
  searchMovements(searchTerm: $term, limit: $limit) {
    id_
    name
    shortVideoUrl
  }
}
"""

async def search_movement_id_by_name(name: str) -> Optional[dict]:
  async with httpx.AsyncClient(timeout=10) as client:
    resp = await client.post(MOVEMENTS_GRAPHQL_URL, json={"query": SEARCH_QUERY, "variables": {"term": name, "limit": 1}})
    resp.raise_for_status()
    data = resp.json().get("data", {})
    arr = data.get("searchMovements", [])
    return (arr[0] if arr else None)

async def backfill():
  engine = create_async_engine(DATABASE_URL, future=True)
  async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
  async with async_session() as session:
    result = await session.execute(select(MovementTemplateModel).where(MovementTemplateModel.movement_id.is_(None)))
    rows = result.scalars().all()
    updated = 0
    for mov in rows:
      match = await search_movement_id_by_name(mov.name)
      if not match:
        continue
      mov.movement_id = match.get("id_")
      if not mov.video_url and match.get("shortVideoUrl"):
        mov.video_url = match.get("shortVideoUrl")
      updated += 1
    await session.commit()
    print(f"Backfill complete. Updated {updated} movement templates.")

if __name__ == "__main__":
  asyncio.run(backfill()) 