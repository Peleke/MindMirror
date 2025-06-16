import logging
import os
from pathlib import Path
from typing import List, Optional

from google.api_core.exceptions import NotFound
from google.cloud import storage

logger = logging.getLogger(__name__)


class GCSClient:
    """
    A client to interact with Google Cloud Storage (GCS) or a local filesystem emulator.

    In production (USE_GCS_EMULATOR=false), it uses Google's Application
    Default Credentials. For local development, set USE_GCS_EMULATOR=true
    and GCS_BUCKET_NAME to a local path (e.g., './gcs_bucket').
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GCSClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.use_emulator = os.getenv("USE_GCS_EMULATOR", "true").lower() == "true"
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "local_gcs_bucket")

        if self.use_emulator:
            self.local_bucket_path = Path(self.bucket_name)
            self.local_bucket_path.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"Using local GCS emulator at: {self.local_bucket_path.resolve()}"
            )
        else:
            if not self.bucket_name:
                raise ValueError(
                    "GCS_BUCKET_NAME must be set when not using the emulator."
                )
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(self.bucket_name)
            logger.info(f"Connected to GCS bucket: {self.bucket_name}")

    def list_files(self, prefix: str) -> List[storage.Blob]:
        """Lists files in the bucket with a given prefix."""
        if self.use_emulator:
            prefix_path = self.local_bucket_path / prefix
            if not prefix_path.exists():
                return []

            # Create mock Blob objects for local files
            blobs = []
            for file_path in prefix_path.rglob("*"):
                if file_path.is_file():
                    mock_blob = storage.Blob(
                        name=str(file_path.relative_to(self.local_bucket_path)),
                        bucket=self.bucket_name,
                    )
                    mock_blob.path = str(file_path.resolve())
                    blobs.append(mock_blob)
            return blobs
        else:
            return list(self.storage_client.list_blobs(self.bucket, prefix=prefix))

    def download_to_filename(self, blob_name: str, destination_filename: str):
        """Downloads a blob to a local file."""
        if self.use_emulator:
            source_path = self.local_bucket_path / blob_name
            if not source_path.exists():
                raise NotFound(f"Local file not found: {blob_name}")
            with open(source_path, "rb") as f_in, open(
                destination_filename, "wb"
            ) as f_out:
                f_out.write(f_in.read())
        else:
            blob = self.bucket.blob(blob_name)
            blob.download_to_filename(destination_filename)

    def upload_from_string(self, destination_blob_name: str, data: str):
        """Uploads data from a string to a blob."""
        if self.use_emulator:
            destination_path = self.local_bucket_path / destination_blob_name
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            destination_path.write_text(data, encoding="utf-8")
        else:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_string(data, content_type="application/json")


def get_gcs_client() -> GCSClient:
    """Singleton factory for the GCSClient."""
    return GCSClient()
