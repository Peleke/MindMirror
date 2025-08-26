import uuid
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from practices.domain.models import DomainSet
from practices.repository.models import SetModel

# Import BlobRepository if/when SetRepository handles direct uploads
# from .blob_repository import GCSBlobRepository


class SetRepository:
    def __init__(self, session: AsyncSession, blob_repository: Optional[Any] = None):
        """Initialize the sets repository.
        Args:
            session (AsyncSession): SQLAlchemy async session
            blob_repository (Optional[GCSBlobRepository]): Repository for blob storage (e.g., GCS)
                                                        Used if sets can have associated media like videos.
        """
        self.session = session
        self.blob_repository = blob_repository  # Store for potential use

    async def create_set(self, set_data: dict) -> DomainSet:
        # prescribed_movement_id must be provided in set_data
        new_set = SetModel(**set_data)
        self.session.add(new_set)
        await self.session.commit()  # Commit directly as it's a simple entity
        await self.session.refresh(new_set)
        return DomainSet.model_validate(new_set)

    async def get_set_by_id(self, set_id: uuid.UUID) -> Optional[DomainSet]:
        stmt = select(SetModel).where(SetModel.id_ == set_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        return DomainSet.model_validate(record) if record else None

    async def list_sets_by_prescribed_movement_id(
        self, prescribed_movement_id: uuid.UUID, limit: Optional[int] = None
    ) -> List[DomainSet]:
        stmt = (
            select(SetModel)
            .where(SetModel.prescribed_movement_id == prescribed_movement_id)
            .order_by(SetModel.position)  # Assuming 'order' field exists
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainSet.model_validate(record) for record in records]

    async def list_all_sets(self) -> List[DomainSet]:
        stmt = select(SetModel).order_by(SetModel.created_at.desc())
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return [DomainSet.model_validate(record) for record in records]

    async def update_set(self, set_id: uuid.UUID, update_data: dict) -> Optional[DomainSet]:
        stmt = select(SetModel).where(SetModel.id_ == set_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return None

        # video_url update logic involving blob_repository would go here if needed
        # e.g., if update_data contains new video file data:
        # if "video_file" in update_data and self.blob_repository:
        #     video_file_data = update_data.pop("video_file")
        #     content_type = update_data.pop("video_content_type", "video/mp4")
        #     # Delete old video if exists and URI is known
        #     # if record.video_url:
        #     #     await self.blob_repository.delete(record.video_url)
        #     record.video_url = await self.blob_repository.create(video_file_data, content_type=content_type)

        for key, value in update_data.items():
            if hasattr(record, key):
                setattr(record, key, value)

        await self.session.commit()
        await self.session.refresh(record)
        return DomainSet.model_validate(record)

    async def delete_set(self, set_id: uuid.UUID) -> bool:
        stmt = select(SetModel).where(SetModel.id_ == set_id)
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()

        if record:
            # If video_url exists and needs to be deleted from GCS:
            # if record.video_url and self.blob_repository:
            #     try:
            #         # Parse bucket_path from record.video_url correctly for delete method
            #         # parsed_url = urlparse(record.video_url)
            #         # bucket_path_to_delete = parsed_url.path.lstrip("/").split("/", 1)[1]
            #         # await self.blob_repository.delete(bucket_path_to_delete)
            #     except Exception as e:
            #         # Log error but proceed with DB deletion
            #         print(f"Error deleting blob {record.video_url} for set {set_id}: {e}")
            await self.session.delete(record)
            await self.session.commit()
            return True
        return False
