#!/usr/bin/env python3
"""
Basic test to verify celery-worker setup

This file tests both the legacy Celery endpoints and the new Pub/Sub endpoints.
The legacy endpoints are deprecated and will be removed in a future version.
"""
import asyncio
import httpx
import time
import json


async def test_celery_worker():
    """Test the celery-worker health endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8002/health")
            print(f"Health check status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error connecting to celery-worker: {e}")
            return False


async def test_legacy_task_submission():
    """Test submitting a task to the legacy celery-worker endpoint (DEPRECATED)"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8002/tasks/index-journal-entry",
                json={
                    "entry_id": "test-entry-123",
                    "user_id": "test-user-456",
                    "tradition": "canon-default",
                },
                headers={"X-Reindex-Secret": "test-secret"},
            )
            print(f"Legacy task submission status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200  # Changed from 202 since it's now a mock task
        except Exception as e:
            print(f"Error submitting legacy task: {e}")
            return False


async def test_pubsub_endpoint():
    """Test the new Pub/Sub endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            # Create a mock Pub/Sub message
            message_data = {
                "entry_id": "test-entry-456",
                "user_id": "test-user-789",
                "tradition": "canon-default",
                "task_type": "journal_indexing",
            }
            
            # Simulate Pub/Sub push message
            response = await client.post(
                "http://localhost:8002/pubsub/journal-indexing",
                content=json.dumps(message_data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Message-Id": "test-message-id",
                },
            )
            print(f"Pub/Sub endpoint status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error testing Pub/Sub endpoint: {e}")
            return False


async def main():
    print("Testing celery-worker...")

    # Wait a bit for services to start
    print("Waiting for services to start...")
    await asyncio.sleep(5)

    # Test health endpoint
    health_ok = await test_celery_worker()
    if not health_ok:
        print("❌ Health check failed")
        return

    print("✅ Health check passed")

    # Test legacy task submission (deprecated)
    legacy_task_ok = await test_legacy_task_submission()
    if not legacy_task_ok:
        print("❌ Legacy task submission failed")
        return

    print("✅ Legacy task submission passed")

    # Test new Pub/Sub endpoint
    pubsub_ok = await test_pubsub_endpoint()
    if not pubsub_ok:
        print("❌ Pub/Sub endpoint test failed")
        return

    print("✅ Pub/Sub endpoint test passed")
    print("🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
