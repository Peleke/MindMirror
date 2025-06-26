"""
Custom exceptions for prompt management system.

This module defines specific exception types for different error scenarios
in the prompt management system.
"""

from typing import Optional, Dict, Any


class PromptError(Exception):
    """Base exception for all prompt-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class PromptNotFoundError(PromptError):
    """Raised when a prompt is not found in storage."""
    
    def __init__(self, message: str, name: Optional[str] = None, version: Optional[str] = None):
        details = {}
        if name:
            details['name'] = name
        if version:
            details['version'] = version
        
        super().__init__(message, details)


class PromptValidationError(PromptError):
    """Raised when prompt validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = value
        
        super().__init__(message, details)


class PromptStorageError(PromptError):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, backend: Optional[str] = None):
        details = {}
        if operation:
            details['operation'] = operation
        if backend:
            details['backend'] = backend
        
        super().__init__(message, details)


class PromptRenderError(PromptError):
    """Raised when prompt rendering fails."""
    
    def __init__(self, message: str, template_name: Optional[str] = None, variables: Optional[Dict[str, Any]] = None):
        details = {}
        if template_name:
            details['template_name'] = template_name
        if variables:
            details['variables'] = variables
        
        super().__init__(message, details)


class PromptVersionError(PromptError):
    """Raised when version-related operations fail."""
    
    def __init__(self, message: str, name: Optional[str] = None, version: Optional[str] = None, available_versions: Optional[list] = None):
        details = {}
        if name:
            details['name'] = name
        if version:
            details['version'] = version
        if available_versions:
            details['available_versions'] = available_versions
        
        super().__init__(message, details)


class PromptCacheError(PromptError):
    """Raised when caching operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, cache_key: Optional[str] = None):
        details = {}
        if operation:
            details['operation'] = operation
        if cache_key:
            details['cache_key'] = cache_key
        
        super().__init__(message, details)


class PromptConfigError(PromptError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, config_value: Optional[Any] = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        if config_value is not None:
            details['config_value'] = config_value
        
        super().__init__(message, details)


class PromptSerializationError(PromptError):
    """Raised when serialization/deserialization fails."""
    
    def __init__(self, message: str, format_type: Optional[str] = None, data: Optional[Any] = None):
        details = {}
        if format_type:
            details['format_type'] = format_type
        if data is not None:
            details['data'] = data
        
        super().__init__(message, details)


class PromptPermissionError(PromptError):
    """Raised when permission is denied for an operation."""
    
    def __init__(self, message: str, operation: Optional[str] = None, resource: Optional[str] = None):
        details = {}
        if operation:
            details['operation'] = operation
        if resource:
            details['resource'] = resource
        
        super().__init__(message, details)


class PromptConcurrencyError(PromptError):
    """Raised when concurrent access conflicts occur."""
    
    def __init__(self, message: str, resource: Optional[str] = None, conflicting_operation: Optional[str] = None):
        details = {}
        if resource:
            details['resource'] = resource
        if conflicting_operation:
            details['conflicting_operation'] = conflicting_operation
        
        super().__init__(message, details)


class PromptQuotaError(PromptError):
    """Raised when quota limits are exceeded."""
    
    def __init__(self, message: str, quota_type: Optional[str] = None, limit: Optional[int] = None, current: Optional[int] = None):
        details = {}
        if quota_type:
            details['quota_type'] = quota_type
        if limit is not None:
            details['limit'] = limit
        if current is not None:
            details['current'] = current
        
        super().__init__(message, details)


# Legacy exceptions for backward compatibility
class TemplateError(PromptError):
    """Legacy exception for template-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


# Exception mapping for backward compatibility
EXCEPTION_MAPPING = {
    'TemplateError': TemplateError,
    'PromptNotFoundError': PromptNotFoundError,
    'PromptValidationError': PromptValidationError,
    'PromptStorageError': PromptStorageError,
    'PromptRenderError': PromptRenderError,
    'PromptVersionError': PromptVersionError,
    'PromptCacheError': PromptCacheError,
    'PromptConfigError': PromptConfigError,
    'PromptSerializationError': PromptSerializationError,
    'PromptPermissionError': PromptPermissionError,
    'PromptConcurrencyError': PromptConcurrencyError,
    'PromptQuotaError': PromptQuotaError,
}


def get_exception_class(name: str) -> type:
    """Get exception class by name."""
    return EXCEPTION_MAPPING.get(name, PromptError)


def is_prompt_exception(exception: Exception) -> bool:
    """Check if an exception is a prompt-related exception."""
    return isinstance(exception, PromptError) 