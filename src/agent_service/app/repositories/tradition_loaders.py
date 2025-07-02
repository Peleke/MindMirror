"""Strategy pattern for tradition loading."""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

from agent_service.app.repositories.gcs_client import GCSClient

logger = logging.getLogger(__name__)


class TraditionLoader(ABC):
    """Abstract base class for tradition loaders."""

    @abstractmethod
    def list_traditions(self) -> List[str]:
        """List all available traditions."""
        pass

    @abstractmethod
    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific tradition."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the loader is healthy."""
        pass


class GCSTraditionLoader(TraditionLoader):
    """GCS-first tradition loader."""

    def __init__(self, gcs_client: GCSClient = None):
        """Initialize GCS tradition loader."""
        self.gcs_client = gcs_client or GCSClient()

    def list_traditions(self) -> List[str]:
        """List all traditions available in GCS."""
        return self.gcs_client.list_traditions()

    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific tradition from GCS."""
        return self.gcs_client.get_tradition_documents(tradition)

    def health_check(self) -> bool:
        """Check if GCS is accessible."""
        return self.gcs_client.health_check()


class LocalTraditionLoader(TraditionLoader):
    """Local files fallback loader."""

    def __init__(self, data_dir: str = None):
        """Initialize local tradition loader."""
        self.data_dir = Path(
            data_dir or os.getenv("TRADITION_DATA_DIR", "/app/local_gcs_bucket")
        )

    def list_traditions(self) -> List[str]:
        """List all traditions available in local files."""
        try:
            if not self.data_dir.exists():
                logger.warning(f"Local data directory does not exist: {self.data_dir}")
                return []

            traditions = []
            for item in self.data_dir.iterdir():
                if item.is_dir():
                    # Check if it has documents subdirectory or direct files
                    docs_dir = item / "documents"
                    if (
                        docs_dir.exists()
                        or any(item.glob("*.pdf"))
                        or any(item.glob("*.txt"))
                    ):
                        traditions.append(item.name)

            logger.info(f"Found traditions in local files: {traditions}")
            return traditions

        except Exception as e:
            logger.error(f"Failed to list traditions from local files: {e}")
            return []

    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific tradition from local files."""
        try:
            documents = []
            tradition_dir = self.data_dir / tradition

            if not tradition_dir.exists():
                logger.warning(f"Tradition directory does not exist: {tradition_dir}")
                return []

            # Check for documents subdirectory first
            docs_dir = tradition_dir / "documents"
            if docs_dir.exists():
                scan_dir = docs_dir
            else:
                # Legacy: scan tradition directory directly
                scan_dir = tradition_dir

            # Scan for PDF and text files
            for file_path in scan_dir.glob("*.pdf"):
                documents.append(
                    {
                        "name": f"{tradition}/{file_path.name}",
                        "size": file_path.stat().st_size,
                        "content_type": "application/pdf",
                        "tradition": tradition,
                        "local_path": str(file_path),
                    }
                )

            for file_path in scan_dir.glob("*.txt"):
                documents.append(
                    {
                        "name": f"{tradition}/{file_path.name}",
                        "size": file_path.stat().st_size,
                        "content_type": "text/plain",
                        "tradition": tradition,
                        "local_path": str(file_path),
                    }
                )

            logger.info(
                f"Found {len(documents)} documents for tradition '{tradition}' in local files"
            )
            return documents

        except Exception as e:
            logger.error(
                f"Failed to get documents for tradition '{tradition}' from local files: {e}"
            )
            return []

    def health_check(self) -> bool:
        """Check if local files are accessible."""
        try:
            return self.data_dir.exists() and self.data_dir.is_dir()
        except Exception as e:
            logger.error(f"Local files health check failed: {e}")
            return False


class HybridTraditionLoader(TraditionLoader):
    """GCS-first with local fallback tradition loader."""

    def __init__(
        self,
        gcs_loader: GCSTraditionLoader = None,
        local_loader: LocalTraditionLoader = None,
    ):
        """Initialize hybrid tradition loader."""
        self.gcs_loader = gcs_loader or GCSTraditionLoader()
        self.local_loader = local_loader or LocalTraditionLoader()

    def list_traditions(self) -> List[str]:
        """List traditions, trying GCS first, then local fallback."""
        try:
            # Try GCS first
            gcs_traditions = self.gcs_loader.list_traditions()
            if gcs_traditions:
                logger.info(f"Found traditions in GCS: {gcs_traditions}")
                return gcs_traditions
        except Exception as e:
            logger.warning(
                f"GCS tradition discovery failed, falling back to local: {e}"
            )

        # Fallback to local
        local_traditions = self.local_loader.list_traditions()
        logger.info(f"Using local traditions as fallback: {local_traditions}")
        return local_traditions

    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        """Get documents for a tradition, trying GCS first, then local fallback."""
        try:
            # Try GCS first
            gcs_documents = self.gcs_loader.get_tradition_documents(tradition)
            if gcs_documents:
                logger.info(
                    f"Found {len(gcs_documents)} documents in GCS for tradition '{tradition}'"
                )
                return gcs_documents
        except Exception as e:
            logger.warning(
                f"GCS document discovery failed for '{tradition}', falling back to local: {e}"
            )

        # Fallback to local
        local_documents = self.local_loader.get_tradition_documents(tradition)
        logger.info(
            f"Using local documents as fallback for tradition '{tradition}': {len(local_documents)} documents"
        )
        return local_documents

    def health_check(self) -> bool:
        """Check if either GCS or local files are accessible."""
        gcs_healthy = self.gcs_loader.health_check()
        local_healthy = self.local_loader.health_check()

        if gcs_healthy:
            logger.info("GCS is healthy")
            return True
        elif local_healthy:
            logger.info("Local files are healthy (GCS unavailable)")
            return True
        else:
            logger.error("Neither GCS nor local files are accessible")
            return False


def create_tradition_loader(mode: str = None) -> TraditionLoader:
    """Factory function to create the appropriate tradition loader."""
    mode = mode or os.getenv("TRADITION_DISCOVERY_MODE", "gcs-first")

    if mode == "gcs-only":
        logger.info("Creating GCS-only tradition loader")
        return GCSTraditionLoader()
    elif mode == "local-only":
        logger.info("Creating local-only tradition loader")
        return LocalTraditionLoader()
    elif mode == "gcs-first":
        logger.info("Creating GCS-first with local fallback tradition loader")
        return HybridTraditionLoader()
    else:
        logger.warning(
            f"Unknown tradition discovery mode '{mode}', defaulting to gcs-first"
        )
        return HybridTraditionLoader()
