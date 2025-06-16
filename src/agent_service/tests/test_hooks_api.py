from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_trigger_reindex_success(client):
    """
    Tests successful triggering of the re-indexing endpoint.
    """
    secret = "test-secret"
    with patch.dict("os.environ", {"REINDEX_SECRET_KEY": secret}):
        with patch("agent_service.web.hooks.celery_app.send_task") as mock_send_task:
            async for test_client in client:
                response = await test_client.post(
                    "/triggers/reindex-tradition",
                    params={"tradition": "canon-default"},
                    headers={"X-Reindex-Secret": secret},
                )

                assert response.status_code == 202
                assert response.json() == {
                    "message": "Accepted re-indexing task for tradition: canon-default"
                }
                mock_send_task.assert_called_once_with(
                    "rebuild_tradition_knowledge_base", args=["canon-default"]
                )


@pytest.mark.asyncio
async def test_trigger_reindex_invalid_secret(client):
    """
    Tests that the endpoint returns 401 Unauthorized with an invalid secret.
    """
    with patch.dict("os.environ", {"REINDEX_SECRET_KEY": "correct-secret"}):
        async for test_client in client:
            response = await test_client.post(
                "/triggers/reindex-tradition",
                params={"tradition": "canon-default"},
                headers={"X-Reindex-Secret": "wrong-secret"},
            )
            assert response.status_code == 401


@pytest.mark.asyncio
async def test_trigger_reindex_missing_secret_header(client):
    """
    Tests that the endpoint returns 422 Unprocessable Entity if the secret header is missing.
    FastAPI treats missing required headers as a validation error.
    """
    with patch.dict("os.environ", {"REINDEX_SECRET_KEY": "any-secret"}):
        async for test_client in client:
            response = await test_client.post(
                "/triggers/reindex-tradition",
                params={"tradition": "canon-default"},
                # No X-Reindex-Secret header
            )
            assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_trigger_reindex_task_queue_fails(client):
    """
    Tests that the endpoint returns 500 Internal Server Error if queuing the task fails.
    """
    secret = "test-secret"
    with patch.dict("os.environ", {"REINDEX_SECRET_KEY": secret}):
        with patch(
            "agent_service.web.hooks.celery_app.send_task",
            side_effect=Exception("Queueing failed"),
        ):
            async for test_client in client:
                response = await test_client.post(
                    "/triggers/reindex-tradition",
                    params={"tradition": "canon-default"},
                    headers={"X-Reindex-Secret": secret},
                )
                assert response.status_code == 500
                assert response.json() == {"detail": "Failed to queue re-indexing task"}
