from typing import Any, Dict, List, Optional
from uuid import UUID

from practices.domain.models import DomainSet
from practices.repository.repositories import (  # Changed from Any to GCSBlobRepository
    GCSBlobRepository,
    SetRepository,
)


class SetService:
    def __init__(self, repository: SetRepository, blob_repository: Optional[GCSBlobRepository] = None):
        self.repository = repository
        self.blob_repository = blob_repository

    async def create_set(self, set_data: Dict[str, Any]) -> DomainSet:
        """Creates a new set. Expects prescribed_movement_id in set_data."""
        # Video upload handling would be here if 'video_file' is in set_data
        # Example:
        # if "video_file" in set_data and self.blob_repository:
        #     video_file_data = set_data.pop("video_file")
        #     content_type = set_data.pop("video_content_type", "video/mp4")
        #     set_data["video_url"] = await self.blob_repository.create(video_file_data, content_type=content_type)
        return await self.repository.create_set(set_data)

    async def get_set_by_id(self, set_id: UUID) -> Optional[DomainSet]:
        return await self.repository.get_set_by_id(set_id)

    async def list_sets_for_movement(
        self, prescribed_movement_id: UUID, limit: Optional[int] = None
    ) -> List[DomainSet]:
        return await self.repository.list_sets_by_prescribed_movement_id(prescribed_movement_id, limit=limit)

    async def list_all_sets(self) -> List[DomainSet]:
        return await self.repository.list_all_sets()

    async def update_set(self, set_id: UUID, update_data: Dict[str, Any]) -> Optional[DomainSet]:
        """Updates a set. Video upload/update logic can be added here."""
        # Example video update logic (similar to swae-be reference):
        # if "video_file" in update_data and self.blob_repository:
        #     video_file_data = update_data.pop("video_file")
        #     content_type = update_data.pop("video_content_type", "video/mp4")

        #     # Get existing set to check for old video_url to delete
        #     existing_set = await self.repository.get_set_by_id(set_id)
        #     old_video_uri = None
        #     if existing_set and existing_set.video_url:
        #         # Convert public URL to gs:// URI or path if needed for delete method
        #         old_video_uri = existing_set.video_url # Placeholder - adjust based on delete method needs

        #     update_data["video_url"] = await self.blob_repository.create(
        #         video_file_data,
        #         uri=None, # Let GCSBlobRepository generate a new name/path
        #         content_type=content_type
        #     )

        #     if old_video_uri:
        #         try:
        #             await self.blob_repository.delete(old_video_uri)
        #         except Exception as e:
        #             print(f"Error deleting old blob {old_video_uri}: {e}") # Log and continue

        return await self.repository.update_set(set_id, update_data)

    async def delete_set(self, set_id: UUID) -> bool:
        """Deletes a set. Also handles deleting associated video from GCS if applicable."""
        # set_to_delete = await self.repository.get_set_by_id(set_id)
        # if set_to_delete and set_to_delete.video_url and self.blob_repository:
        #     try:
        #         # Convert public URL to gs:// URI or path if needed for delete method
        #         await self.blob_repository.delete(set_to_delete.video_url)
        #     except Exception as e:
        #         print(f"Error deleting blob {set_to_delete.video_url} for set {set_id}: {e}")
        # Decide if failure to delete blob should prevent DB deletion.
        # Generally, DB deletion should proceed, and blob deletion failure logged.
        return await self.repository.delete_set(set_id)
