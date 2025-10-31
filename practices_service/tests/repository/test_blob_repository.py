import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from practices.repository.repositories.blob_repository import GCSBlobRepository

# Assuming your Config is at practices.web.config
# If it's elsewhere, adjust the import path for the patch
# from practices.web.config import Config


@pytest.fixture
def mock_gcs_client_and_bucket():
    with patch("google.cloud.storage.Client") as MockClient, patch("practices.web.config.Config") as MockConfig:
        # Configure MockConfig attributes used by GCSBlobRepository
        MockConfig.GCP_PROJECT_ID = "test-gcp-project"

        mock_client_instance = MockClient.return_value
        mock_bucket_instance = MagicMock()
        mock_client_instance.get_bucket.return_value = mock_bucket_instance

        # Mock blob operations
        mock_blob_instance = MagicMock()
        mock_bucket_instance.blob.return_value = mock_blob_instance

        # Ensure upload_from_string, delete, generate_signed_url are MagicMock
        # if they need specific return values or side effects not covered by default.
        # For basic calls, MagicMock default behavior might be enough.
        mock_blob_instance.generate_signed_url.return_value = "https://fake-signed-url.com/blob"

        yield mock_client_instance, mock_bucket_instance, mock_blob_instance, MockConfig


@pytest.mark.asyncio
class TestGCSBlobRepository:
    TEST_BUCKET_NAME = "test-bucket"
    TEST_BLOB_PATH = "test_folder/test_file.txt"
    TEST_FILE_DATA = b"Hello, GCS!"
    TEST_CONTENT_TYPE = "text/plain"
    TEST_GS_URI = f"gs://{TEST_BUCKET_NAME}/{TEST_BLOB_PATH}"
    TEST_PUBLIC_URL = f"https://storage.googleapis.com/{TEST_BUCKET_NAME}/{TEST_BLOB_PATH}"

    async def test_create_blob_without_uri(self, mock_gcs_client_and_bucket):
        _, mock_bucket, mock_blob, _ = mock_gcs_client_and_bucket
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)

        public_url = await repo.create(file_data=self.TEST_FILE_DATA, content_type=self.TEST_CONTENT_TYPE)

        mock_bucket.blob.assert_called_once()
        # Path will be <uuid>.txt because no URI was provided
        created_blob_path = mock_bucket.blob.call_args[0][0]
        assert "." + self.TEST_CONTENT_TYPE.split("/")[-1] in created_blob_path
        mock_blob.upload_from_string.assert_called_once_with(self.TEST_FILE_DATA, content_type=self.TEST_CONTENT_TYPE)
        assert public_url.startswith(f"https://storage.googleapis.com/{self.TEST_BUCKET_NAME}/")

    async def test_create_blob_with_uri(self, mock_gcs_client_and_bucket):
        _, mock_bucket, mock_blob, _ = mock_gcs_client_and_bucket
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)

        public_url = await repo.create(
            file_data=self.TEST_FILE_DATA, uri=self.TEST_GS_URI, content_type=self.TEST_CONTENT_TYPE
        )

        mock_bucket.blob.assert_called_once_with(self.TEST_BLOB_PATH)
        mock_blob.upload_from_string.assert_called_once_with(self.TEST_FILE_DATA, content_type=self.TEST_CONTENT_TYPE)
        assert public_url == self.TEST_PUBLIC_URL

    async def test_delete_blob_by_path(self, mock_gcs_client_and_bucket):
        _, mock_bucket, mock_blob, _ = mock_gcs_client_and_bucket
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)

        result = await repo.delete(self.TEST_BLOB_PATH)
        assert result is True
        mock_bucket.blob.assert_called_once_with(self.TEST_BLOB_PATH)
        mock_blob.delete.assert_called_once()

    async def test_delete_blob_by_gs_uri(self, mock_gcs_client_and_bucket):
        _, mock_bucket, mock_blob, _ = mock_gcs_client_and_bucket
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)

        result = await repo.delete(self.TEST_GS_URI)
        assert result is True
        mock_bucket.blob.assert_called_once_with(self.TEST_BLOB_PATH)
        mock_blob.delete.assert_called_once()

    async def test_delete_blob_by_public_url(self, mock_gcs_client_and_bucket):
        _, mock_bucket, mock_blob, _ = mock_gcs_client_and_bucket
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)

        result = await repo.delete(self.TEST_PUBLIC_URL)
        assert result is True
        mock_bucket.blob.assert_called_once_with(self.TEST_BLOB_PATH)
        mock_blob.delete.assert_called_once()

    async def test_update_blob(self, mock_gcs_client_and_bucket):
        _, mock_bucket, mock_blob, _ = mock_gcs_client_and_bucket
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)
        updated_data = b"New content"

        public_url = await repo.update(
            file_data=updated_data, uri=self.TEST_GS_URI, content_type=self.TEST_CONTENT_TYPE
        )

        mock_bucket.blob.assert_called_once_with(self.TEST_BLOB_PATH)
        mock_blob.upload_from_string.assert_called_once_with(updated_data, content_type=self.TEST_CONTENT_TYPE)
        assert public_url == self.TEST_PUBLIC_URL

    async def test_get_blob_public_url(self, mock_gcs_client_and_bucket):
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)
        url = await repo.get_blob_url(self.TEST_BLOB_PATH)
        assert url == self.TEST_PUBLIC_URL

    async def test_get_signed_url(self, mock_gcs_client_and_bucket):
        _, _, mock_blob, _ = mock_gcs_client_and_bucket  # mock_blob has generate_signed_url mocked
        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)

        signed_url = await repo.get_signed_url(self.TEST_BLOB_PATH, expiration_minutes=30)

        mock_blob.generate_signed_url.assert_called_once()
        # Check that timedelta was passed with correct minutes
        args, kwargs = mock_blob.generate_signed_url.call_args
        assert kwargs["expiration"].total_seconds() == 30 * 60
        assert signed_url == "https://fake-signed-url.com/blob"

    # Add tests for error conditions, like blob not found on delete, invalid URIs, etc.
    async def test_delete_blob_not_found(self, mock_gcs_client_and_bucket):
        _, mock_bucket, mock_blob, _ = mock_gcs_client_and_bucket
        # Simulate GCS not found error
        from google.cloud.exceptions import (
            NotFound,  # Import here as it might not always be available
        )

        mock_blob.delete.side_effect = NotFound("Blob not found")

        repo = GCSBlobRepository(bucket_name=self.TEST_BUCKET_NAME)
        result = await repo.delete(self.TEST_BLOB_PATH)
        assert result is False
        mock_blob.delete.assert_called_once()
