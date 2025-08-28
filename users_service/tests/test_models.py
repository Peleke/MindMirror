"""Basic tests for users service models."""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from users.repository.models import (
    SchedulableModel,
    ServiceEnum,
    ServiceModel,
    UserModel,
    UserServicesModel,
)


@pytest.mark.asyncio
async def test_user_model_creation(dbsession: AsyncSession):
    user_id = uuid.uuid4()
    supabase_id = f"supabase_test_{user_id}"
    user = UserModel(id_=user_id, supabase_id=supabase_id)
    dbsession.add(user)
    await dbsession.flush()  # Use flush to get DB-side defaults like created_at
    await dbsession.refresh(user)

    assert user.id_ == user_id
    assert user.supabase_id == supabase_id
    assert user.created_at is not None
    assert user.modified_at is not None


@pytest.mark.asyncio
async def test_service_model_creation(dbsession: AsyncSession):
    service = ServiceModel(name=ServiceEnum.MEALS, description="Test service description")  # Use Enum for name
    dbsession.add(service)
    await dbsession.flush()
    await dbsession.refresh(service)

    assert service.id_ is not None  # id_ is auto-generated UUID
    assert service.name == ServiceEnum.MEALS
    assert service.description == "Test service description"
    assert service.created_at is not None


@pytest.mark.asyncio
async def test_service_model_name_uniqueness(dbsession: AsyncSession):
    service1 = ServiceModel(name=ServiceEnum.PRACTICE, description="Service 1")
    dbsession.add(service1)
    await dbsession.flush()

    service2 = ServiceModel(name=ServiceEnum.PRACTICE, description="Service 2 attempting same name")
    dbsession.add(service2)
    with pytest.raises(IntegrityError):  # Expecting unique constraint violation
        await dbsession.flush()
    await dbsession.rollback()  # Rollback failed transaction


@pytest.mark.asyncio
async def test_user_service_link_creation(dbsession: AsyncSession):
    # Create a user
    user = UserModel(supabase_id="test_user_for_link")
    dbsession.add(user)
    await dbsession.flush()
    await dbsession.refresh(user)

    # Create a service
    service = ServiceModel(name=ServiceEnum.SHADOW_BOXING, description="Shadow Boxing Training")
    dbsession.add(service)
    await dbsession.flush()
    await dbsession.refresh(service)

    # Create link
    link = UserServicesModel(user_id=user.id_, service_id=service.id_)
    dbsession.add(link)
    await dbsession.flush()
    await dbsession.refresh(link)

    assert link.user_id == user.id_
    assert link.service_id == service.id_
    assert link.active is True  # Default value
    assert link.created_at is not None


@pytest.mark.asyncio
async def test_schedulable_model_creation(dbsession: AsyncSession):
    # Create a user
    user = UserModel(supabase_id="test_user_for_schedulable")
    dbsession.add(user)
    await dbsession.flush()
    await dbsession.refresh(user)

    # Create a service
    service = ServiceModel(name=ServiceEnum.PROGRAMS, description="Training Programs")
    dbsession.add(service)
    await dbsession.flush()
    await dbsession.refresh(service)

    # Create schedulable
    entity_id = uuid.uuid4()
    schedulable = SchedulableModel(
        user_id=user.id_,
        service_id=service.id_,
        name="Complete Week 1 Program",
        description="Follow the program guide for week 1.",
        entity_id=entity_id,
        completed=False,
    )
    dbsession.add(schedulable)
    await dbsession.flush()
    await dbsession.refresh(schedulable)

    assert schedulable.id_ is not None
    assert schedulable.user_id == user.id_
    assert schedulable.service_id == service.id_
    assert schedulable.name == "Complete Week 1 Program"
    assert schedulable.entity_id == entity_id
    assert schedulable.completed is False
    assert schedulable.created_at is not None


def test_service_enum_values():
    """Test that all expected service enum values exist."""
    expected_services = ["meals", "practice", "shadow_boxing", "fitness_db", "programs"]
    actual_services = [service.value for service in ServiceEnum]

    for expected in expected_services:
        assert expected in actual_services
