import logging
import os
from typing import List, Optional
from google.cloud import storage

logger = logging.getLogger(__name__)


class GCSClient:
    """Google Cloud Storage client for tradition documents."""

    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv(
            "GCS_BUCKET_NAME", "local_gcs_bucket"
        )
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
        logger.info(f"Initialized GCS client with bucket: {self.bucket_name}")

    def list_files(self, prefix: str = None) -> List[str]:
        """List files in the GCS bucket with optional prefix."""
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            files = [blob.name for blob in blobs]
            logger.info(f"Found {len(files)} files in bucket {self.bucket_name}")
            return files
        except Exception as e:
            logger.error(f"Failed to list files in bucket {self.bucket_name}: {e}")
            return []

    def download_to_filename(self, blob_name: str, filename: str) -> bool:
        """Download a blob to a local filename."""
        try:
            blob = self.bucket.blob(blob_name)
            blob.download_to_filename(filename)
            logger.info(f"Downloaded {blob_name} to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            return False

    def upload_from_string(self, blob_name: str, content: str) -> bool:
        """Upload a string to a blob."""
        try:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(content)
            logger.info(f"Uploaded content to {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to {blob_name}: {e}")
            return False

    def get_blob(self, blob_name: str) -> Optional[storage.Blob]:
        """Get a blob by name."""
        try:
            return self.bucket.blob(blob_name)
        except Exception as e:
            logger.error(f"Failed to get blob {blob_name}: {e}")
            return None


# Global client instance
_gcs_client: Optional[GCSClient] = None


def get_gcs_client() -> GCSClient:
    """Create or get the global GCS client instance."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = GCSClient()
    return _gcs_client
