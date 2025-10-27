import uuid
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple
from urllib.parse import urlparse

# Attempt to import google.cloud.storage, but allow it to fail gracefully
# if the dependency isn't installed, as it's specific to GCSBlobRepository.
# The application should ensure this is installed if GCSBlobRepository is used.
try:
    from google.cloud import storage  # type: ignore
except ImportError:
    storage = None  # type: ignore

from practices.web.config import Config  # Assuming config is in practices.web


class BlobRepository(ABC):
    """
    Abstract base class for blob storage repositories.
    """

    @abstractmethod
    async def create(self, file_data: bytes, uri: Optional[str] = None, content_type: Optional[str] = None) -> str:
        """Create a new blob."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, blob_uri_or_path: str) -> bool:
        """Delete a blob."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, file_data: bytes, uri: str, content_type: Optional[str] = None) -> str:
        """Update an existing blob."""
        raise NotImplementedError

    @abstractmethod
    async def get_blob_url(self, bucket_path: str) -> str:
        """Get a public URL for a blob given its path."""
        raise NotImplementedError

    @abstractmethod
    async def get_signed_url(self, bucket_path: str, expiration_minutes: int = 15) -> str:
        """Get a signed URL for temporary access to a blob."""
        raise NotImplementedError


class GCSBlobRepository(BlobRepository):
    """
    Google Cloud Storage implementation of the BlobRepository.
    """

    def __init__(self, bucket_name: str, gcs_project_id: Optional[str] = None):
        if storage is None:
            raise RuntimeError(
                "google-cloud-storage library is not installed. "
                "Please install it to use GCSBlobRepository (e.g., `poetry add google-cloud-storage`)"
            )
        self.client = storage.Client(project=gcs_project_id or Config.GCP_PROJECT_ID)
        self._bucket_name = bucket_name
        try:
            self.bucket = self.client.get_bucket(self._bucket_name)
        except Exception as e:  # Catch a more general exception for bucket not found or access issues
            # Consider logging this error
            # Depending on use case, might want to create bucket if not exists:
            # self.bucket = self.client.create_bucket(self._bucket_name)
            # print(f"Bucket {self._bucket_name} did not exist. It has been created.")
            raise RuntimeError(f"Failed to get GCS bucket '{self._bucket_name}'. Original error: {e}")

    def _parse_gcs_uri(self, uri: str) -> Tuple[str, str]:
        """Parses a GCS URI (gs://bucket/path/to/blob) into bucket name and blob path."""
        parsed = urlparse(uri)
        if parsed.scheme != "gs":
            raise ValueError(f"Invalid GCS URI scheme: {uri}. Must be 'gs://'")
        bucket_name = parsed.netloc
        blob_path = parsed.path.lstrip("/")
        return bucket_name, blob_path

    def _extract_blob_path_from_public_url(self, url: str) -> str:
        """Extracts the blob path from a public GCS URL."""
        # Example URL: https://storage.googleapis.com/your-bucket-name/path/to/your/blob.txt
        # Needs to remove "https://storage.googleapis.com/your-bucket-name/"
        parsed = urlparse(url)
        if not parsed.netloc.endswith("storage.googleapis.com"):
            raise ValueError(f"URL '{url}' is not a recognized GCS public URL.")
        # The path part starts with a leading '/', then bucket name, then blob path.
        # Example: /my-bucket/path/to/blob.txt
        path_parts = parsed.path.lstrip("/").split("/", 1)
        if len(path_parts) < 2 or path_parts[0] != self._bucket_name:
            raise ValueError(f"URL '{url}' does not match the configured bucket '{self._bucket_name}'.")
        return path_parts[1]

    async def create(self, file_data: bytes, uri: Optional[str] = None, content_type: Optional[str] = None) -> str:
        bucket_path: str
        if uri:
            _, bucket_path = self._parse_gcs_uri(uri)  # Expects gs://bucket/path
        else:
            extension = content_type.split("/")[-1] if content_type else "bin"
            filename = f"{uuid.uuid4()}.{extension}"
            bucket_path = filename  # Store at root by default, or specify a path convention

        blob = self.bucket.blob(bucket_path)
        # In a real async environment, this should use an async upload method.
        # google-cloud-storage client library's blob.upload_from_string is synchronous.
        # For a truly async operation, you might need to run this in a thread pool executor.
        # For simplicity in this example, we call it directly.
        blob.upload_from_string(file_data, content_type=content_type)
        return f"https://storage.googleapis.com/{self._bucket_name}/{bucket_path}"

    async def delete(self, blob_uri_or_path: str) -> bool:
        blob_path: str
        if blob_uri_or_path.startswith("gs://"):
            bucket_name, path = self._parse_gcs_uri(blob_uri_or_path)
            if bucket_name != self._bucket_name:
                raise ValueError(f"URI bucket '{bucket_name}' does not match configured bucket '{self._bucket_name}'.")
            blob_path = path
        elif blob_uri_or_path.startswith("https://storage.googleapis.com/"):
            blob_path = self._extract_blob_path_from_public_url(blob_uri_or_path)
        else:
            blob_path = blob_uri_or_path  # Assume it's a direct path if no scheme

        blob = self.bucket.blob(blob_path)
        try:
            # blob.delete() is synchronous
            blob.delete()
            return True
        except Exception as e:  # google.cloud.exceptions.NotFound if blob doesn't exist
            print(f"Error deleting blob gs://{self._bucket_name}/{blob_path}: {e}")
            return False

    async def update(self, file_data: bytes, uri: str, content_type: Optional[str] = None) -> str:
        # GCS update is effectively an overwrite, so same as create but URI must point to existing blob path.
        if not uri.startswith("gs://"):
            raise ValueError("Update URI must be a gs:// URI pointing to the blob to replace.")

        bucket_name, blob_path = self._parse_gcs_uri(uri)
        if bucket_name != self._bucket_name:
            raise ValueError(f"URI bucket '{bucket_name}' does not match configured bucket '{self._bucket_name}'.")

        blob = self.bucket.blob(blob_path)
        blob.upload_from_string(file_data, content_type=content_type)
        return f"https://storage.googleapis.com/{self._bucket_name}/{blob_path}"

    async def get_blob_url(self, bucket_path: str) -> str:
        return f"https://storage.googleapis.com/{self._bucket_name}/{bucket_path}"

    async def get_signed_url(self, bucket_path: str, expiration_minutes: int = 15) -> str:
        import datetime

        blob = self.bucket.blob(bucket_path)
        signed_url = blob.generate_signed_url(
            version="v4", expiration=datetime.timedelta(minutes=expiration_minutes), method="GET"
        )
        return signed_url
