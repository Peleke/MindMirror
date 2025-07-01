#!/usr/bin/env python3
"""
Basic test to verify celery-worker setup
"""
import asyncio
import httpx
import time


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


async def test_task_submission():
    """Test submitting a task to celery-worker"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8002/tasks/index-journal-entry",
                json={
                    "entry_id": "test-entry-123",
                    "user_id": "test-user-456",
                    "tradition": "canon-default",
                },
            )
            print(f"Task submission status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 202
        except Exception as e:
            print(f"Error submitting task: {e}")
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

    # Test task submission
    task_ok = await test_task_submission()
    if not task_ok:
        print("❌ Task submission failed")
        return

    print("✅ Task submission passed")
    print("🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
