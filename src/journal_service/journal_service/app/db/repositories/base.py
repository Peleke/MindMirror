from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from journal_service.journal_service.app.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """Base repository with common CRUD operations."""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
    
    async def get(self, id: str) -> Optional[ModelType]:
        """Get entity by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def list(self, limit: int = 100, offset: int = 0) -> List[ModelType]:
        """List entities with pagination."""
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new entity."""
        entity = self.model(**kwargs)
        self.session.add(entity)
        await self.session.flush()
        return entity
    
    async def update(self, id: str, **kwargs) -> Optional[ModelType]:
        """Update an entity."""
        entity = await self.get(id)
        if not entity:
            return None
        
        for key, value in kwargs.items():
            setattr(entity, key, value)
        
        await self.session.flush()
        return entity
    
    async def delete(self, id: str) -> bool:
        """Delete an entity."""
        entity = await self.get(id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        return True 