from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from habits_service.habits_service.app.db.tables import TemplateAccess, TemplateProvenance


class TemplateAccessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def grant(
        self,
        *,
        kind: str,
        template_id: str,
        permission: str,
        user_id: Optional[str] = None,
    ) -> TemplateAccess:
        tid = uuid.UUID(str(template_id))
        obj = TemplateAccess(
            kind=kind,
            template_id=tid,
            user_id=user_id,
            permission=permission,
        )
        self.session.add(obj)
        try:
            await self.session.flush()
            return obj
        except IntegrityError:
            await self.session.rollback()
            # Return existing
            res = await self.session.execute(
                select(TemplateAccess).where(
                    and_(
                        TemplateAccess.kind == kind,
                        TemplateAccess.template_id == tid,
                        (TemplateAccess.user_id == user_id),
                        TemplateAccess.permission == permission,
                    )
                )
            )
            existing = res.scalars().first()
            if existing:
                return existing
            # Re-raise if something else
            raise

    async def revoke(self, access_id: str) -> bool:
        aid = uuid.UUID(str(access_id))
        res = await self.session.execute(delete(TemplateAccess).where(TemplateAccess.id == aid))
        return (res.rowcount or 0) > 0

    async def upsert_public_view(self, *, kind: str, template_id: str) -> TemplateAccess:
        # Public view is user_id NULL and permission 'view'
        tid = uuid.UUID(str(template_id))
        res = await self.session.execute(
            select(TemplateAccess).where(
                and_(
                    TemplateAccess.kind == kind,
                    TemplateAccess.template_id == tid,
                    TemplateAccess.user_id.is_(None),
                    TemplateAccess.permission == "view",
                )
            )
        )
        existing = res.scalars().first()
        if existing:
            return existing
        return await self.grant(kind=kind, template_id=str(tid), permission="view", user_id=None)

    async def list_accessible_template_ids(self, *, kind: str, user_id: Optional[str]) -> List[str]:
        # accessible = public view OR any grant for user
        res = await self.session.execute(
            select(TemplateAccess.template_id).where(
                and_(
                    TemplateAccess.kind == kind,
                    or_(
                        TemplateAccess.user_id == user_id,
                        TemplateAccess.user_id.is_(None),
                    ),
                )
            )
        )
        return [str(r[0]) for r in res.all()]


class TemplateProvenanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(
        self,
        *,
        kind: str,
        template_id: str,
        origin: str,
        origin_user_id: Optional[str] = None,
    ) -> TemplateProvenance:
        tid = uuid.UUID(str(template_id))
        res = await self.session.execute(
            select(TemplateProvenance).where(
                and_(
                    TemplateProvenance.kind == kind,
                    TemplateProvenance.template_id == tid,
                )
            )
        )
        existing = res.scalars().first()
        if existing:
            existing.origin = origin
            existing.origin_user_id = origin_user_id
            await self.session.flush()
            return existing
        obj = TemplateProvenance(
            kind=kind,
            template_id=tid,
            origin=origin,
            origin_user_id=origin_user_id,
        )
        self.session.add(obj)
        await self.session.flush()
        return obj


