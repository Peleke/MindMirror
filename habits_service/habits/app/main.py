from fastapi import FastAPI, Header, HTTPException
from habits.app.api.models import AutoEnrollRequest, RedeemRequest
from strawberry.fastapi import GraphQLRouter
import strawberry
from habits.app.db.session import engine
from habits.app.db.models import Base
from habits.app.graphql.schemas.query import Query as RootQuery
from habits.app.graphql.schemas.mutation import Mutation as RootMutation
from habits.app.config import get_settings
from sqlalchemy import text
from habits.app.graphql.context import get_context


schema = strawberry.Schema(query=RootQuery, mutation=RootMutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(graphql_app, prefix="/graphql")


@app.post("/api/auto-enroll")
async def auto_enroll(entitlements: AutoEnrollRequest, x_internal_id: str = Header(None)):
    if not x_internal_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        email = entitlements.email
        items = entitlements.entitlements or []

        from datetime import date
        from habits.app.db.uow import UnitOfWork
        from habits.app.db.repositories.write import ProgramAssignmentWriteRepository

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
    try:
        code = body.code
        entitlement = body.entitlement
        if entitlement.code != code or entitlement.status != "issued" or not entitlement.programTemplateId:
            raise HTTPException(status_code=400, detail="invalid-code")

        from datetime import date
        from habits.app.db.uow import UnitOfWork
        from habits.app.db.repositories.write import ProgramAssignmentWriteRepository

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


@app.post("/api/unenroll")
async def unenroll(program_template_id: str, x_internal_id: str = Header(None)):
    if not x_internal_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        from habits.app.db.uow import UnitOfWork
        from habits.app.db.repositories.write_structural import UserProgramAssignmentRepository
        async with UnitOfWork() as uow:
            repo = UserProgramAssignmentRepository(uow.session)
            # Find active assignment and set status to cancelled
            # Simplify: update any active assignment for this user/program
            from sqlalchemy import select
            from habits.app.db.tables import UserProgramAssignment
            import uuid
            pid = uuid.UUID(str(program_template_id))
            res = await uow.session.execute(
                select(UserProgramAssignment).where(
                    UserProgramAssignment.user_id == x_internal_id,
                    UserProgramAssignment.program_template_id == pid,
                    UserProgramAssignment.status == "active",
                )
            )
            obj = res.scalars().first()
            if not obj:
                return {"ok": True, "changed": 0}
            obj.status = "cancelled"
            await uow.session.flush()
            await uow.session.commit()
            return {"ok": True, "changed": 1}
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
            # Backfill columns added post-migration until Alembic is in place
            await conn.execute(text("""
                ALTER TABLE habits.lesson_templates
                ADD COLUMN IF NOT EXISTS subtitle TEXT NULL;
            """))
            await conn.execute(text("""
                ALTER TABLE habits.lesson_templates
                ADD COLUMN IF NOT EXISTS hero_image_url VARCHAR NULL;
            """))
            await conn.execute(text("""
                ALTER TABLE habits.habit_templates
                ADD COLUMN IF NOT EXISTS hero_image_url VARCHAR NULL;
            """))
            await conn.execute(text("""
                ALTER TABLE habits.program_templates
                ADD COLUMN IF NOT EXISTS subtitle TEXT NULL;
            """))
            await conn.execute(text("""
                ALTER TABLE habits.program_templates
                ADD COLUMN IF NOT EXISTS hero_image_url VARCHAR NULL;
            """))
    except Exception:
        # Do not crash service on startup if perms are insufficient
        pass


