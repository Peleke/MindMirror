"""
Enhanced data models for prompt management.

This module provides data classes and models for managing prompt templates
with versioning, validation, and serialization support.
"""

import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

from .exceptions import PromptValidationError


class StoreType(Enum):
    """Enumeration of supported storage backends."""
    LOCAL = "local"
    GCS = "gcs"
    MEMORY = "memory"
    FIRESTORE = "firestore"


@dataclass
class PromptInfo:
    """
    Information about a registered prompt.
    
    This class represents a complete prompt template with metadata,
    versioning information, and validation.
    """
    
    name: str
    version: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    variables: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate the prompt info after initialization."""
        self._validate()
        self._extract_variables()
    
    def _validate(self):
        """Validate prompt info fields."""
        if not self.name or not isinstance(self.name, str):
            raise PromptValidationError("Prompt name must be a non-empty string")
        
        if not self._is_valid_name(self.name):
            raise PromptValidationError(f"Invalid prompt name: {self.name}")
        
        if not self.version or not isinstance(self.version, str):
            raise PromptValidationError("Version must be a non-empty string")
        
        if not self._is_valid_version(self.version):
            raise PromptValidationError(f"Invalid version format: {self.version}")
        
        if not self.content or not isinstance(self.content, str):
            raise PromptValidationError("Content must be a non-empty string")
        
        if not isinstance(self.metadata, dict):
            raise PromptValidationError("Metadata must be a dictionary")
        
        if not isinstance(self.variables, list):
            raise PromptValidationError("Variables must be a list")
        
        # Validate timestamps
        try:
            datetime.fromisoformat(self.created_at)
            datetime.fromisoformat(self.updated_at)
        except ValueError:
            raise PromptValidationError("Invalid timestamp format")
    
    def _is_valid_name(self, name: str) -> bool:
        """Check if prompt name is valid."""
        # Allow alphanumeric, hyphens, underscores, and dots
        pattern = r'^[a-zA-Z0-9._-]+$'
        return bool(re.match(pattern, name)) and len(name) <= 100
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version string is valid."""
        # Allow semantic versioning format: major.minor.patch or just major
        pattern = r'^\d+(\.\d+(\.\d+)?)?$'
        return bool(re.match(pattern, version))
    
    def _extract_variables(self):
        """Extract variables from template content if not provided."""
        if not self.variables:
            # Simple regex to find Jinja2 variables
            variable_pattern = r'\{\{\s*(\w+)\s*\}\}'
            matches = re.findall(variable_pattern, self.content)
            self.variables = list(set(matches))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptInfo':
        """Create PromptInfo from dictionary."""
        return cls(**data)
    
    def update_content(self, new_content: str) -> 'PromptInfo':
        """Create a new PromptInfo with updated content."""
        return PromptInfo(
            name=self.name,
            version=self._increment_version(),
            content=new_content,
            metadata=self.metadata.copy(),
            created_at=self.created_at,
            updated_at=datetime.now().isoformat()
        )
    
    def update_metadata(self, new_metadata: Dict[str, Any]) -> 'PromptInfo':
        """Create a new PromptInfo with updated metadata."""
        return PromptInfo(
            name=self.name,
            version=self._increment_version(),
            content=self.content,
            metadata=new_metadata,
            variables=self.variables.copy(),
            created_at=self.created_at,
            updated_at=datetime.now().isoformat()
        )
    
    def _increment_version(self) -> str:
        """Increment the minor version number."""
        try:
            parts = self.version.split('.')
            if len(parts) >= 2:
                major, minor = parts[0], parts[1]
                new_minor = str(int(minor) + 1)
                return f"{major}.{new_minor}"
            else:
                return f"{self.version}.1"
        except (ValueError, IndexError):
            return "1.1"
    
    def __eq__(self, other: Any) -> bool:
        """Compare two PromptInfo objects."""
        if not isinstance(other, PromptInfo):
            return False
        
        return (
            self.name == other.name and
            self.version == other.version and
            self.content == other.content
        )
    
    def __hash__(self) -> int:
        """Hash based on name and version."""
        return hash((self.name, self.version))


@dataclass
class PromptConfig:
    """
    Configuration for prompt service.
    
    This class holds configuration settings for the prompt service,
    including storage backend selection and caching options.
    """
    
    store_type: StoreType
    store_path: Optional[str] = None
    gcs_bucket: Optional[str] = None
    gcs_prefix: str = "prompts/"
    firestore_collection: Optional[str] = None
    cache_size: int = 1000
    cache_ttl: int = 3600  # seconds
    enable_validation: bool = True
    enable_caching: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate configuration settings."""
        if not isinstance(self.store_type, StoreType):
            raise PromptValidationError("store_type must be a StoreType enum")
        
        # Only validate required fields if they are provided
        if self.store_type == StoreType.LOCAL and self.store_path is None:
            raise PromptValidationError("store_path is required for LOCAL store type")
        
        if self.store_type == StoreType.GCS and self.gcs_bucket is None:
            raise PromptValidationError("gcs_bucket is required for GCS store type")
        
        if self.store_type == StoreType.FIRESTORE and self.firestore_collection is None:
            raise PromptValidationError("firestore_collection is required for FIRESTORE store type")
        
        if self.cache_size < 1:
            raise PromptValidationError("cache_size must be at least 1")
        
        if self.cache_ttl < 0:
            raise PromptValidationError("cache_ttl must be non-negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'store_type': self.store_type.value,
            'store_path': self.store_path,
            'gcs_bucket': self.gcs_bucket,
            'gcs_prefix': self.gcs_prefix,
            'firestore_collection': self.firestore_collection,
            'cache_size': self.cache_size,
            'cache_ttl': self.cache_ttl,
            'enable_validation': self.enable_validation,
            'enable_caching': self.enable_caching
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptConfig':
        """Create PromptConfig from dictionary."""
        # Convert store_type string back to enum
        if 'store_type' in data and isinstance(data['store_type'], str):
            data['store_type'] = StoreType(data['store_type'])
        
        return cls(**data)


@dataclass
class PromptSearchCriteria:
    """
    Criteria for searching prompts.
    
    This class defines search criteria for finding prompts
    based on various attributes.
    """
    
    name_pattern: Optional[str] = None
    version_pattern: Optional[str] = None
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    content_pattern: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    limit: Optional[int] = None
    offset: int = 0
    
    def __post_init__(self):
        """Validate search criteria after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate search criteria."""
        if self.limit is not None and self.limit < 1:
            raise PromptValidationError("limit must be at least 1")
        
        if self.offset < 0:
            raise PromptValidationError("offset must be non-negative")
        
        if self.limit is not None and self.offset >= self.limit:
            raise PromptValidationError("offset must be less than limit")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'name_pattern': self.name_pattern,
            'version_pattern': self.version_pattern,
            'metadata_filters': self.metadata_filters,
            'content_pattern': self.content_pattern,
            'limit': self.limit,
            'offset': self.offset
        }
        
        # Convert datetime objects to ISO strings
        if self.created_after:
            result['created_after'] = self.created_after.isoformat()
        if self.created_before:
            result['created_before'] = self.created_before.isoformat()
        if self.updated_after:
            result['updated_after'] = self.updated_after.isoformat()
        if self.updated_before:
            result['updated_before'] = self.updated_before.isoformat()
        
        return result


@dataclass
class PromptStats:
    """
    Statistics about prompt usage and storage.
    
    This class provides metrics about prompt operations
    and storage utilization.
    """
    
    total_prompts: int = 0
    total_versions: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    render_count: int = 0
    storage_size_bytes: int = 0
    last_updated: Optional[datetime] = None
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self.cache_hits + self.cache_misses
        return self.cache_hits / total_requests if total_requests > 0 else 0.0
    
    @property
    def average_versions_per_prompt(self) -> float:
        """Calculate average versions per prompt."""
        return self.total_versions / self.total_prompts if self.total_prompts > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        if self.last_updated:
            result['last_updated'] = self.last_updated.isoformat()
        return result


class StorageConfig(BaseModel):
    """
    Configuration for storage backends.
    
    This model defines the configuration options for different
    storage backends (local, GCS, etc.).
    """
    
    storage_type: str = Field(..., description="Type of storage backend (local, gcs)")
    local_path: Optional[str] = Field(None, description="Local file system path for local storage")
    gcs_bucket: Optional[str] = Field(None, description="GCS bucket name for GCS storage")
    gcs_credentials: Optional[str] = Field(None, description="Path to GCS credentials file")
    
    @validator('storage_type')
    def validate_storage_type(cls, v):
        """Validate storage type."""
        valid_types = ['local', 'gcs']
        if v not in valid_types:
            raise ValueError(f"storage_type must be one of {valid_types}")
        return v
    
    @validator('local_path')
    def validate_local_path(cls, v, values):
        """Validate local path is provided for local storage."""
        if values.get('storage_type') == 'local' and not v:
            raise ValueError("local_path is required for local storage")
        return v
    
    @validator('gcs_bucket')
    def validate_gcs_bucket(cls, v, values):
        """Validate GCS bucket is provided for GCS storage."""
        if values.get('storage_type') == 'gcs' and not v:
            raise ValueError("gcs_bucket is required for GCS storage")
        return v
    
    @validator('gcs_credentials')
    def validate_gcs_credentials(cls, v, values):
        """Validate GCS credentials are provided for GCS storage."""
        if values.get('storage_type') == 'gcs' and not v:
            raise ValueError("gcs_credentials is required for GCS storage")
        return v 