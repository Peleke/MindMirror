from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Literal
import time
from strawberry.fastapi import GraphQLRouter
import strawberry
from habits_service.habits_service.app.db.session import engine
from habits_service.habits_service.app.db.models import Base
from habits_service.habits_service.app.graphql.schemas.query import Query as RootQuery
from habits_service.habits_service.app.graphql.schemas.mutation import Mutation as RootMutation
from habits_service.habits_service.app.config import get_settings
from sqlalchemy import text
from habits_service.habits_service.app.graphql.context import get_context


schema = strawberry.Schema(query=RootQuery, mutation=RootMutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(graphql_app, prefix="/graphql")


# --- Simple in-memory rate limiter (per user, per endpoint) ---
_RATE_LIMIT: dict[str, tuple[int, int]] = {"/api/auto-enroll": (5, 60), "/api/redeem": (5, 60)}
_RATE_BUCKETS: dict[str, List[float]] = {}


def _check_rate_limit(endpoint: str, user_id: str):
    limit, window = _RATE_LIMIT.get(endpoint, (10, 60))
    key = f"{endpoint}:{user_id}"
    now = time.time()
    bucket = _RATE_BUCKETS.get(key, [])
    # drop old timestamps
    bucket = [ts for ts in bucket if now - ts <= window]
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="rate-limited")
    bucket.append(now)
    _RATE_BUCKETS[key] = bucket


# --- Request models ---
class EntitlementItem(BaseModel):
    status: Literal["issued", "redeemed", "revoked"]
    email: EmailStr
    programTemplateId: str
    code: Optional[str] = None


class AutoEnrollRequest(BaseModel):
    email: EmailStr
    entitlements: List[EntitlementItem]


class RedeemRequest(BaseModel):
    code: str
    entitlement: EntitlementItem


@app.post("/api/auto-enroll")
async def auto_enroll(entitlements: AutoEnrollRequest, x_internal_id: str = Header(None)):
    if not x_internal_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    _check_rate_limit("/api/auto-enroll", x_internal_id)
    try:
        email = entitlements.email
        items = entitlements.entitlements or []

        from datetime import date
        from habits_service.habits_service.app.db.uow import UnitOfWork
        from habits_service.habits_service.app.db.repositories.write import ProgramAssignmentWriteRepository

        today = date.today()
        assigned: list[str] = []
        async with UnitOfWork() as uow:
            w = ProgramAssignmentWriteRepository(uow.session)
            for e in items:
                if e.status == "issued" and e.email.lower() == email.lower() and e.programTemplateId:
                    await w.assign_program_to_user(user_id=x_internal_id, program_template_id=e.programTemplateId, start_date=today)
                    assigned.append(e.programTemplateId)
            await uow.session.commit()
        return {"ok": True, "assigned": assigned}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="failed")


@app.post("/api/redeem")
async def redeem(body: RedeemRequest, x_internal_id: str = Header(None)):
    if not x_internal_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    _check_rate_limit("/api/redeem", x_internal_id)
    try:
        code = body.code
        entitlement = body.entitlement
        if entitlement.code != code or entitlement.status != "issued" or not entitlement.programTemplateId:
            raise HTTPException(status_code=400, detail="invalid-code")

        from datetime import date
        from habits_service.habits_service.app.db.uow import UnitOfWork
        from habits_service.habits_service.app.db.repositories.write import ProgramAssignmentWriteRepository

        today = date.today()
        async with UnitOfWork() as uow:
            w = ProgramAssignmentWriteRepository(uow.session)
            await w.assign_program_to_user(user_id=x_internal_id, program_template_id=entitlement.programTemplateId, start_date=today)
            await uow.session.commit()
        return {"ok": True, "programTemplateId": entitlement.programTemplateId}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="failed")


@app.on_event("startup")
async def ensure_schema_exists():
    # Create schema if not present (optional, works on Postgres when user has perms)
    # This is best-effort; Alembic will manage tables later.
    try:
        async with engine.begin() as conn:
            schema = get_settings().database_schema
            # Ensure schema exists first (dev convenience)
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        # Do not crash service on startup if perms are insufficient
        pass


