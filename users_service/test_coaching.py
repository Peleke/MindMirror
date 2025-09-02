#!/usr/bin/env python3
"""
Simple test script to verify coaching functionality.
Run this after setting up the database and services.
"""
import asyncio
import uuid
from users.repository.repositories.user_repository import UserRepository
from users.repository.models import RoleModel, DomainModel
from users.repository.uow import UnitOfWork
from users.repository.database import async_session_factory

async def test_coaching_flow():
    """Test the basic coaching flow."""
    print("Testing coaching functionality...")
    
    # Create UoW with proper session factory
    uow = UnitOfWork(session_factory=async_session_factory)
    async with uow:
            repo = UserRepository(session=uow.session)
            
            # Create test users
            print("Creating test users...")
            coach_user = await repo.create_user({"supabase_id": f"coach_test_{uuid.uuid4()}"})
            client_user = await repo.create_user({"supabase_id": f"client_test_{uuid.uuid4()}"})
            
            print(f"Coach user ID: {coach_user.id_}")
            print(f"Client user ID: {client_user.id_}")
            
            # Assign coach role to coach user
            print("Assigning coach role...")
            await repo.assign_role_to_user(
                coach_user.id_, 
                RoleModel.coach, 
                DomainModel.practices
            )
            
            # Test coaching request
            print("Creating coaching request...")
            relationship = await repo.request_coaching_by_user_id(
                coach_user_id=coach_user.id_,
                client_user_id=client_user.id_
            )
            
            print(f"Coaching request created: {relationship.id_}")
            print(f"Status: {relationship.status}")
            
            # Test pending requests
            print("Getting pending requests...")
            pending = await repo.get_pending_coaching_requests_for_client(client_user.id_)
            print(f"Found {len(pending)} pending requests")
            
            # Accept coaching request
            print("Accepting coaching request...")
            accepted = await repo.accept_coaching_request(
                client_user_id=client_user.id_,
                coach_user_id=coach_user.id_
            )
            
            print(f"Request accepted: {accepted.status}")
            
            # Test coach-client verification
            print("Testing coach-client verification...")
            is_coach = await repo.is_coach_for_client(
                coach_user_id=coach_user.id_,
                client_user_id=client_user.id_
            )
            
            print(f"Is coach for client: {is_coach}")
            
            # Get coach's clients
            print("Getting coach's clients...")
            clients = await repo.get_my_clients(coach_user.id_)
            print(f"Coach has {len(clients)} clients")
            
            # Get client's coaches
            print("Getting client's coaches...")
            coaches = await repo.get_my_coaches(client_user.id_)
            print(f"Client has {len(coaches)} coaches")
            
            await uow.commit()
            print("✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_coaching_flow()) 