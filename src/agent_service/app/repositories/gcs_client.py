"""GCS client for tradition discovery and document access."""

import logging
import os
from typing import List, Dict, Any, Optional

from google.cloud import storage
from google.cloud.exceptions import NotFound

logger = logging.getLogger(__name__)


class GCSClient:
    """Client for interacting with Google Cloud Storage (emulator or real)."""

    def __init__(self, bucket_name: str = None):
        """Initialize GCS client."""
        self.bucket_name = bucket_name or os.getenv(
            "GCS_BUCKET_NAME", "local_gcs_bucket"
        )

        # Check if we're using emulator
        emulator_host = os.getenv("STORAGE_EMULATOR_HOST")
        if emulator_host:
            logger.info(f"Using GCS emulator at {emulator_host}")
            # For emulator, we don't need credentials
            self.client = storage.Client()
        else:
            logger.info("Using real GCS")
            # For real GCS, credentials should be set via GOOGLE_APPLICATION_CREDENTIALS
            self.client = storage.Client()

        self.bucket = None
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if necessary."""
        try:
            self.bucket = self.client.bucket(self.bucket_name)
            # Check if bucket exists
            self.bucket.reload()
            logger.info(f"Using existing bucket: {self.bucket_name}")
        except NotFound:
            logger.info(f"Creating bucket: {self.bucket_name}")
            self.bucket = self.client.create_bucket(self.bucket_name)

    def list_traditions(self) -> List[str]:
        """List all traditions available in GCS."""
        try:
            traditions = set()

            # List all blobs in the bucket
            blobs = self.client.list_blobs(self.bucket_name)

            for blob in blobs:
                # Extract tradition name from path
                # Expected structures:
                # 1. tradition_name/file.pdf (direct structure)
                # 2. file.txt (flat structure - treat as 'default' tradition)
                # 3. subdirectory/file.txt (use bucket name as tradition)
                path_parts = blob.name.split("/")

                if len(path_parts) == 1:
                    # Flat structure: file.txt -> tradition = 'default'
                    traditions.add("default")
                elif len(path_parts) >= 2:
                    # Check if first part is a subdirectory (like 'documents')
                    if path_parts[0] in ["documents", "files"]:
                        # Subdirectory structure: documents/file.txt -> use bucket name as tradition
                        tradition = self.bucket_name
                        traditions.add(tradition)
                    else:
                        # Direct structure: tradition_name/file.pdf
                        tradition = path_parts[0]
                        traditions.add(tradition)

            logger.info(f"Found traditions in GCS: {list(traditions)}")
            return list(traditions)

        except Exception as e:
            logger.error(f"Failed to list traditions from GCS: {e}")
            return []

    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific tradition."""
        try:
            documents = []

            # Determine prefix based on tradition
            if tradition == "default":
                # For default tradition, look for files without prefix
                prefix = ""
            elif tradition == self.bucket_name:
                # For bucket-named tradition, look for documents/ or files/ subdirectory
                prefix = "documents/"
                # Try files/ if documents/ doesn't exist
                test_blobs = list(
                    self.client.list_blobs(
                        self.bucket_name, prefix=prefix, max_results=1
                    )
                )
                if not test_blobs:
                    prefix = "files/"
            else:
                # For named traditions, look for tradition/ prefix
                prefix = f"{tradition}/"

            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)

            for blob in blobs:
                # Skip directories
                if blob.name.endswith("/"):
                    continue

                document = {
                    "name": blob.name,
                    "size": blob.size,
                    "updated": blob.updated,
                    "content_type": blob.content_type,
                    "tradition": tradition,
                }
                documents.append(document)

            logger.info(f"Found {len(documents)} documents for tradition '{tradition}'")
            return documents

        except Exception as e:
            logger.error(f"Failed to get documents for tradition '{tradition}': {e}")
            return []

    def download_document(self, blob_name: str) -> Optional[bytes]:
        """Download a document from GCS."""
        try:
            blob = self.bucket.blob(blob_name)
            content = blob.download_as_bytes()
            logger.debug(f"Downloaded document: {blob_name}")
            return content
        except Exception as e:
            logger.error(f"Failed to download document '{blob_name}': {e}")
            return None

    def upload_document(
        self, blob_name: str, content: bytes, content_type: str = None
    ) -> bool:
        """Upload a document to GCS."""
        try:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(content, content_type=content_type)
            logger.info(f"Uploaded document: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload document '{blob_name}': {e}")
            return False

    def health_check(self) -> bool:
        """Check if GCS is accessible."""
        try:
            # Try to list blobs to verify connectivity
            list(self.client.list_blobs(self.bucket_name, max_results=1))
            return True
        except Exception as e:
            logger.error(f"GCS health check failed: {e}")
            return False
