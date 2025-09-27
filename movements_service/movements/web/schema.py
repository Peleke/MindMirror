from typing import List, Optional
from uuid import UUID
import strawberry
from strawberry.types import Info

from ..repository.movements_repo import MovementsRepoPg
from ..repository.database import get_session  # if available in service layer
from ..clients.local_db_client import ExerciseDBLocalClient
from ..clients.exercisedb_api_client import ExerciseDBApiClient
from ..clients.composite_client import CompositeExerciseClient
from ..mappers.external_to_local import external_to_local_row


@strawberry.federation.type(keys=["id_"])
class Movement:
    id_: strawberry.ID
    name: str
    slug: str
    difficulty: Optional[str]
    bodyRegion: Optional[str]
    archetype: Optional[str]
    equipment: List[str]
    primaryMuscles: List[str]
    secondaryMuscles: List[str]
    movementPatterns: List[str]
    planesOfMotion: List[str]
    tags: List[str]
    description: Optional[str]
    shortVideoUrl: Optional[str]
    longVideoUrl: Optional[str]
    isPublic: bool
    userId: Optional[str]

    @classmethod
    def resolve_reference(cls, info: Info, id_: strawberry.ID) -> "Movement":
        repo, _, _ = get_repos(info)
        # Federation resolver expects an entity lookup by key
        # Note: incoming arg name must match key field (id_)
        return map_row_to_movement_async(repo, str(id_))


@strawberry.type
class MovementSearchResult:
    id_: Optional[strawberry.ID] = None
    isExternal: bool = False
    externalId: Optional[str] = None
    name: str = ""
    bodyRegion: Optional[str] = None
    equipment: List[str] = strawberry.field(default_factory=list)
    difficulty: Optional[str] = None
    shortVideoUrl: Optional[str] = None
    imageUrl: Optional[str] = None
    description: Optional[str] = None


@strawberry.input
class MovementCreateInput:
    name: str
    slug: Optional[str] = None
    difficulty: Optional[str] = None
    bodyRegion: Optional[str] = None
    archetype: Optional[str] = None
    equipment: Optional[List[str]] = None
    primaryMuscles: Optional[List[str]] = None
    secondaryMuscles: Optional[List[str]] = None
    movementPatterns: Optional[List[str]] = None
    planesOfMotion: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    shortVideoUrl: Optional[str] = None
    longVideoUrl: Optional[str] = None


@strawberry.input
class MovementUpdateInput:
    name: Optional[str] = None
    slug: Optional[str] = None
    difficulty: Optional[str] = None
    bodyRegion: Optional[str] = None
    archetype: Optional[str] = None
    equipment: Optional[List[str]] = None
    primaryMuscles: Optional[List[str]] = None
    secondaryMuscles: Optional[List[str]] = None
    movementPatterns: Optional[List[str]] = None
    planesOfMotion: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    shortVideoUrl: Optional[str] = None
    longVideoUrl: Optional[str] = None


# Placeholder repo/client abstractions
class MovementsRepository:
    async def get(self, id_: str) -> Optional[dict]:
        return None

    async def search(self, **filters) -> List[dict]:
        return []

    async def create(self, user_id: Optional[str], data: dict) -> dict:
        return {"id_": "temp", **data, "isPublic": user_id is None, "userId": user_id}

    async def update(self, id_: str, data: dict) -> Optional[dict]:
        return None

    async def delete(self, id_: str) -> bool:
        return False


class ExerciseDBClient:
    async def search(self, term: Optional[str], body_region: Optional[str], equipment: Optional[str], limit: int) -> List[dict]:
        return []

    async def fetch(self, external_id: str) -> Optional[dict]:
        return None


def map_row_to_movement(row: dict) -> Movement:
    return Movement(
        id_=strawberry.ID(str(row.get("id_"))),
        name=row.get("name", ""),
        slug=row.get("slug", ""),
        difficulty=row.get("difficulty"),
        bodyRegion=row.get("bodyRegion"),
        archetype=row.get("archetype"),
        equipment=row.get("equipment") or [],
        primaryMuscles=row.get("primaryMuscles") or [],
        secondaryMuscles=row.get("secondaryMuscles") or [],
        movementPatterns=row.get("movementPatterns") or [],
        planesOfMotion=row.get("planesOfMotion") or [],
        tags=row.get("tags") or [],
        description=row.get("description"),
        shortVideoUrl=row.get("shortVideoUrl"),
        longVideoUrl=row.get("longVideoUrl"),
        isPublic=bool(row.get("isPublic", True)),
        userId=row.get("userId"),
    )


async def map_row_to_movement_async(repo: MovementsRepository, id_: str) -> Movement:
    row = await repo.get(id_)
    if not row:
        # Provide a minimal placeholder to avoid federation failures
        return Movement(
            id_=strawberry.ID(id_), name=f"Exercise {id_}", slug=id_, difficulty=None, bodyRegion=None, archetype=None,
            equipment=[], primaryMuscles=[], secondaryMuscles=[], movementPatterns=[], planesOfMotion=[], tags=[],
            shortVideoUrl=None, longVideoUrl=None, isPublic=True, userId=None
        )
    return map_row_to_movement(row)


def map_row_to_search_result(row: dict, is_external: bool = False) -> MovementSearchResult:
    return MovementSearchResult(
        id_=strawberry.ID(str(row["id_"])) if row.get("id_") else None,
        isExternal=is_external,
        externalId=row.get("externalId"),
        name=row.get("name", ""),
        bodyRegion=row.get("bodyRegion"),
        equipment=row.get("equipment") or [],
        difficulty=row.get("difficulty"),
        shortVideoUrl=row.get("shortVideoUrl"),
        imageUrl=(row.get("imageUrl") or row.get("gifUrl")),
        description=row.get("description"),
    )


def get_repos(info: Info) -> tuple[MovementsRepository, ExerciseDBClient, Optional[str]]:
    # Prefer a repository factory that yields a new AsyncSession per resolver to avoid concurrent Session access
    repo_factory = info.context.get("movements_repo_factory")
    if callable(repo_factory):
        repo = repo_factory()
    else:
        repo = info.context.get("movements_repo") or MovementsRepository()
    client: ExerciseDBClient = info.context.get("exercise_client") or ExerciseDBClient()
    user_id: Optional[str] = info.context.get("user_id")
    return repo, client, user_id


@strawberry.type
class Query:
    @strawberry.field(name="movement")
    async def movement(self, info: Info, id: strawberry.ID) -> Optional[Movement]:
        repo, _, _ = get_repos(info)
        row = await repo.get(str(id))
        return map_row_to_movement(row) if row else None

    @strawberry.field(name="searchMovements")
    async def search_movements(
        self,
        info: Info,
        searchTerm: Optional[str] = None,
        bodyRegion: Optional[str] = None,
        pattern: Optional[str] = None,
        equipment: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> List[MovementSearchResult]:
        repo, _, _ = get_repos(info)
        # Build composite client from context or fallbacks
        local_client = ExerciseDBLocalClient(repo=repo) if isinstance(repo, MovementsRepoPg) else ExerciseDBLocalClient(repo)  # type: ignore
        external_client = ExerciseDBApiClient()
        composite = CompositeExerciseClient(local=local_client, external=external_client)
        merged = await composite.search(searchTerm, bodyRegion, equipment, limit, offset)
        out: List[MovementSearchResult] = []
        for r in merged:
            out.append(map_row_to_search_result(r, is_external=(r.get("source") == "exercise_db")))
        return out


@strawberry.type
class Mutation:
    @strawberry.mutation(name="createMovementQuick")
    async def create_movement_quick(self, info: Info, name: str) -> Movement:
        repo, _, user_id = get_repos(info)
        row = await repo.create(user_id, {"name": name, "slug": name.lower().replace(" ", "-")})
        return map_row_to_movement(row)

    @strawberry.mutation(name="createMovement")
    async def create_movement(self, info: Info, input: MovementCreateInput) -> Movement:
        repo, _, user_id = get_repos(info)
        row = await repo.create(user_id, strawberry.asdict(input))
        return map_row_to_movement(row)

    @strawberry.mutation(name="updateMovement")
    async def update_movement(self, info: Info, id: strawberry.ID, input: MovementUpdateInput) -> Optional[Movement]:
        repo, _, user_id = get_repos(info)
        updated = await repo.update(str(id), {k: v for k, v in strawberry.asdict(input).items() if v is not None})
        return map_row_to_movement(updated) if updated else None

    @strawberry.mutation(name="deleteMovement")
    async def delete_movement(self, info: Info, id: strawberry.ID) -> bool:
        repo, _, user_id = get_repos(info)
        return await repo.delete(str(id))

    @strawberry.mutation(name="importExternalMovement")
    async def import_external_movement(self, info: Info, externalId: str) -> Movement:
        repo, _, user_id = get_repos(info)
        api = ExerciseDBApiClient()
        data = await api.get_by_id(externalId)
        if not data:
            raise Exception("NOT_FOUND")
        payload = external_to_local_row(data)
        # Idempotent: check if exists by (source, externalId)
        existing = None
        try:
            # @ts-ignore: repo may be a concrete MovementsRepoPg with helper
            existing = await repo.get_by_external("exercise-db", externalId)  # type: ignore
        except Exception:
            existing = None
        if existing:
            return map_row_to_movement(existing)
        row = await repo.create(user_id, payload)
        return map_row_to_movement(row)


def get_schema() -> strawberry.Schema:
    return strawberry.federation.Schema(query=Query, mutation=Mutation, enable_federation_2=True) 