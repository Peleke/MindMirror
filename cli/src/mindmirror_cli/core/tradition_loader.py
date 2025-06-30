"""Tradition loader for MindMirror CLI (GCS-first, local fallback)."""

import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

try:
    from google.cloud import storage
except ImportError:
    storage = None

logger = logging.getLogger(__name__)

class TraditionLoader(ABC):
    @abstractmethod
    def list_traditions(self) -> List[str]:
        pass

    @abstractmethod
    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

class GCSTraditionLoader(TraditionLoader):
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME", "canon-default")
        self.client = None
        if storage is not None:
            emulator_host = os.getenv("STORAGE_EMULATOR_HOST")
            if emulator_host:
                # Ensure the emulator host has the correct format
                if not emulator_host.startswith(('http://', 'https://')):
                    emulator_host = f"http://{emulator_host}"
                
                # Set the environment variable for the emulator
                os.environ["STORAGE_EMULATOR_HOST"] = emulator_host
                logger.info(f"Using GCS emulator at {emulator_host}")
            else:
                logger.warning("STORAGE_EMULATOR_HOST not set, will try real GCS")
            
            try:
                self.client = storage.Client()
                # Test connection by listing buckets
                buckets = list(self.client.list_buckets())
                logger.info(f"GCS client initialized successfully. Found buckets: {[b.name for b in buckets]}")
            except Exception as e:
                logger.error(f"Failed to initialize GCS client: {e}")
                self.client = None
        else:
            logger.warning("google-cloud-storage not installed; GCS loader will not work.")

    def list_traditions(self) -> List[str]:
        if not self.client:
            return []
        try:
            traditions = set()
            
            # List all buckets
            buckets = list(self.client.list_buckets())
            logger.info(f"Found buckets: {[b.name for b in buckets]}")
            
            # For each bucket, check if it contains tradition data
            for bucket in buckets:
                bucket_name = bucket.name
                logger.info(f"Processing bucket: {bucket_name}")
                
                # Skip system buckets like 'prompts'
                if bucket_name in ['prompts']:
                    logger.info(f"Skipping system bucket: {bucket_name}")
                    continue
                    
                # List objects in the bucket
                blobs = list(self.client.list_blobs(bucket_name))
                logger.info(f"Found {len(blobs)} blobs in bucket {bucket_name}")
                
                for blob in blobs:
                    logger.info(f"Processing blob: {blob.name}")
                    # Extract tradition name from path
                    # Expected structures:
                    # 1. tradition_name/file.pdf (direct structure)
                    # 2. file.txt (flat structure - treat as 'default' tradition)
                    # 3. subdirectory/file.txt (use bucket name as tradition)
                    path_parts = blob.name.split('/')
                    logger.info(f"Path parts: {path_parts}")
                    
                    if len(path_parts) == 1:
                        # Flat structure: file.txt -> tradition = 'default'
                        traditions.add('default')
                        logger.info(f"Added default tradition from flat structure")
                    elif len(path_parts) >= 2:
                        # Check if first part is a subdirectory (like 'documents')
                        if path_parts[0] in ['documents', 'files']:
                            # Subdirectory structure: documents/file.txt -> use bucket name as tradition
                            tradition = bucket_name
                            traditions.add(tradition)
                            logger.info(f"Added tradition from bucket: {tradition}")
                        else:
                            # Direct structure: tradition_name/file.pdf
                            tradition = path_parts[0]
                            traditions.add(tradition)
                            logger.info(f"Added tradition: {tradition}")
            
            logger.info(f"Found traditions in GCS: {list(traditions)}")
            return list(traditions)
            
        except Exception as e:
            logger.error(f"Failed to list traditions from GCS: {e}")
            return []

    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        try:
            documents = []
            
            # List all buckets to find the one with our data
            buckets = list(self.client.list_buckets())
            
            for bucket in buckets:
                bucket_name = bucket.name
                if bucket_name in ['prompts']:
                    continue
                    
                # Determine prefix based on tradition
                if tradition == 'default':
                    # For default tradition, look for files without prefix
                    prefix = ""
                elif tradition == bucket_name:
                    # For bucket-named tradition, look for documents/ or files/ subdirectory
                    prefix = "documents/"
                    # Try files/ if documents/ doesn't exist
                    test_blobs = list(self.client.list_blobs(bucket_name, prefix=prefix, max_results=1))
                    if not test_blobs:
                        prefix = "files/"
                else:
                    # For named traditions, look for tradition/ prefix
                    prefix = f"{tradition}/"
                
                blobs = self.client.list_blobs(bucket_name, prefix=prefix)
                for blob in blobs:
                    if blob.name.endswith('/'):
                        continue
                    documents.append({
                        "name": blob.name,
                        "size": blob.size,
                        "tradition": tradition,
                        "bucket": bucket_name,
                    })
            
            return documents
        except Exception as e:
            logger.error(f"Failed to get documents for tradition '{tradition}': {e}")
            return []

    def health_check(self) -> bool:
        if not self.client:
            return False
        try:
            # Test by listing buckets
            buckets = list(self.client.list_buckets())
            return len(buckets) > 0
        except Exception as e:
            logger.error(f"GCS health check failed: {e}")
            return False

class LocalTraditionLoader(TraditionLoader):
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or os.getenv("TRADITION_DATA_DIR", "./local_gcs_bucket"))

    def list_traditions(self) -> List[str]:
        try:
            if not self.data_dir.exists():
                return []
            traditions = []
            for item in self.data_dir.iterdir():
                if item.is_dir():
                    docs_dir = item / "documents"
                    if docs_dir.exists() or any(item.glob("*.pdf")) or any(item.glob("*.txt")):
                        traditions.append(item.name)
            return traditions
        except Exception as e:
            logger.error(f"Failed to list traditions from local files: {e}")
            return []

    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        try:
            documents = []
            tradition_dir = self.data_dir / tradition
            if not tradition_dir.exists():
                return []
            docs_dir = tradition_dir / "documents"
            scan_dir = docs_dir if docs_dir.exists() else tradition_dir
            for file_path in scan_dir.glob("*.pdf"):
                documents.append({
                    "name": f"{tradition}/{file_path.name}",
                    "size": file_path.stat().st_size,
                    "tradition": tradition,
                    "local_path": str(file_path),
                })
            for file_path in scan_dir.glob("*.txt"):
                documents.append({
                    "name": f"{tradition}/{file_path.name}",
                    "size": file_path.stat().st_size,
                    "tradition": tradition,
                    "local_path": str(file_path),
                })
            return documents
        except Exception as e:
            logger.error(f"Failed to get documents for tradition '{tradition}' from local files: {e}")
            return []

    def health_check(self) -> bool:
        try:
            return self.data_dir.exists() and self.data_dir.is_dir()
        except Exception as e:
            logger.error(f"Local files health check failed: {e}")
            return False

class HybridTraditionLoader(TraditionLoader):
    def __init__(self, gcs_loader: GCSTraditionLoader = None, local_loader: LocalTraditionLoader = None):
        self.gcs_loader = gcs_loader or GCSTraditionLoader()
        self.local_loader = local_loader or LocalTraditionLoader()

    def list_traditions(self) -> List[str]:
        try:
            gcs_traditions = self.gcs_loader.list_traditions()
            if gcs_traditions:
                return gcs_traditions
        except Exception as e:
            logger.warning(f"GCS tradition discovery failed, falling back to local: {e}")
        return self.local_loader.list_traditions()

    def get_tradition_documents(self, tradition: str) -> List[Dict[str, Any]]:
        try:
            gcs_documents = self.gcs_loader.get_tradition_documents(tradition)
            if gcs_documents:
                return gcs_documents
        except Exception as e:
            logger.warning(f"GCS document discovery failed for '{tradition}', falling back to local: {e}")
        return self.local_loader.get_tradition_documents(tradition)

    def health_check(self) -> bool:
        return self.gcs_loader.health_check() or self.local_loader.health_check()

def create_tradition_loader(mode: str = None) -> TraditionLoader:
    mode = mode or os.getenv("TRADITION_DISCOVERY_MODE", "gcs-first")
    if mode == "gcs-only":
        return GCSTraditionLoader()
    elif mode == "local-only":
        return LocalTraditionLoader()
    elif mode == "gcs-first":
        return HybridTraditionLoader()
    else:
        return HybridTraditionLoader() 