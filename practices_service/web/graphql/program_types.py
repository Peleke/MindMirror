import uuid
from datetime import datetime
from typing import List, Optional

import strawberry

from practices.repository.models import (
    PracticeModel,
)
from practices.repository.models import (
    Program as ProgramModel,  # Import models for resolvers
)
from practices.repository.models import ProgramPracticeLink as ProgramPracticeLinkModel
from practices.repository.models import ProgramTag as ProgramTagModel

from .dataloaders import PracticeLoader  # Import the new DataLoader

# Assuming PracticeType is defined elsewhere and can be imported
# This path might need adjustment based on your project structure
from .types import (  # Assuming GQLPractice is your Strawberry type for PracticeModel
    GQLPractice,
    PracticeType,
)


# Placeholder for a generic dataloader or service context
# In a real app, this would come from strawberry.Info.context
class FakeInfoContext:
    def __init__(self):
        # self.practice_loader = PracticeLoader() # Example dataloader
        # self.services = ... # Example services
        pass


class FakeInfo:
    def __init__(self):
        self.context = FakeInfoContext()


# Example of how you might get a service; adapt to your actual DI/service access pattern
# def get_practice_service(info: strawberry.Info):
#     return info.context.services.practice_service


@strawberry.type
class ProgramTagType:
    id: uuid.UUID
    name: str
    created_at: datetime
    modified_at: datetime

    @classmethod
    def from_model(cls, model: ProgramTagModel) -> "ProgramTagType":
        return cls(id=model.id, name=model.name, created_at=model.created_at, modified_at=model.modified_at)


@strawberry.type
class ProgramPracticeLinkType:
    id: uuid.UUID
    # practice_id: uuid.UUID # Expose practice_id if direct ID access is needed by client
    sequence_order: int
    interval_days_after: int
    created_at: datetime
    modified_at: datetime

    _model: strawberry.Private[ProgramPracticeLinkModel]  # For internal model access

    @strawberry.field
    async def practice(self, info: strawberry.Info) -> Optional[GQLPractice]:  # Changed to GQLPractice
        # This resolver fetches the actual Practice object using a DataLoader.

        # The DataLoader should be available in the GraphQL context.
        # The key for the context dictionary ('practice_loader') must match how it's added.
        if "practice_loader" not in info.context:
            # This typically indicates a setup issue where the DataLoader wasn't added to the context.
            # Handle this error appropriately (e.g., log, raise an internal server error).
            # As a temporary fallback for development, you might try direct loading, but this defeats the purpose of DataLoader.
            print("ERROR: PracticeLoader not found in info.context. DataLoader is not configured correctly.")
            # Fallback (less ideal, N+1 potential if used broadly):
            # if self._model.practice: # If it was somehow eager loaded
            #     return GQLPractice.from_model(self._model.practice)
            return None

        practice_loader: PracticeLoader = info.context["practice_loader"]

        try:
            # self._model.practice_id is the key to load.
            # The DataLoader's .load() method is awaitable and returns the PracticeModel or None.
            practice_model = await practice_loader.load(self._model.practice_id)
            if practice_model:
                return GQLPractice.from_model(practice_model)
        except Exception as e:
            # Log the exception details
            print(f"Error loading practice with ID {self._model.practice_id} using DataLoader: {e}")
            # Depending on policy, you might want to raise the error or return None

        return None

    @classmethod
    def from_model(cls, model: ProgramPracticeLinkModel) -> "ProgramPracticeLinkType":
        return cls(
            id=model.id,
            # practice_id=model.practice_id, # If you choose to expose it
            sequence_order=model.sequence_order,
            interval_days_after=model.interval_days_after,
            created_at=model.created_at,
            modified_at=model.modified_at,
            model=model,  # Pass the model instance for the resolver
        )


@strawberry.type
class ProgramType:
    id: uuid.UUID
    name: str
    description: Optional[str]
    level: Optional[str]
    practice_links: List[ProgramPracticeLinkType]
    tags: List[ProgramTagType]
    created_at: datetime
    modified_at: datetime
    # owner: Optional[UserType] # Future

    @strawberry.field
    def practice_count(self) -> int:
        return len(self.practice_links)

    @classmethod
    def from_model(cls, model: ProgramModel) -> "ProgramType":
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            level=model.level,
            practice_links=[ProgramPracticeLinkType.from_model(link) for link in model.practice_links],
            tags=[ProgramTagType.from_model(tag) for tag in model.tags],
            created_at=model.created_at,
            modified_at=model.modified_at,
        )


# --- Input Types ---


@strawberry.input
class ProgramTagInput:
    name: str


@strawberry.input
class ProgramPracticeLinkInput:
    practice_id: uuid.UUID
    sequence_order: int
    interval_days_after: int = 1  # Default interval


@strawberry.input
class ProgramCreateInput:
    name: str
    description: Optional[str] = None
    level: Optional[str] = None
    practice_links: List[ProgramPracticeLinkInput] = strawberry.field(default_factory=list)
    tags: List[ProgramTagInput] = strawberry.field(default_factory=list)


@strawberry.input
class ProgramUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    # For updating links and tags, typically you'd replace the entire list.
    # More granular updates (add/remove specific items) are more complex.
    practice_links: Optional[List[ProgramPracticeLinkInput]] = None
    tags: Optional[List[ProgramTagInput]] = None
