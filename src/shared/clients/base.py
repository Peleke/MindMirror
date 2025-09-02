"""
Base HTTP client with GraphQL support, authentication, and resilience patterns.

This module provides the foundation for all service-to-service communication,
following functional programming principles with composable utilities.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Union
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass(frozen=True)
class ServiceConfig:
    """Immutable configuration for a service client."""
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    service_name: str = "unknown"


@dataclass(frozen=True)
class AuthContext:
    """Authentication context for service requests."""
    user_id: UUID
    service_token: Optional[str] = None
    internal_id_header: Optional[str] = None


class ServiceClientError(Exception):
    """Base exception for service client errors."""
    def __init__(self, message: str, service: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.service = service
        self.status_code = status_code


class ServiceUnavailableError(ServiceClientError):
    """Raised when a service is temporarily unavailable."""
    pass


class AuthenticationError(ServiceClientError):
    """Raised when authentication fails."""
    pass


class DataNotFoundError(ServiceClientError):
    """Raised when requested data is not found."""
    pass


def create_auth_headers(auth: AuthContext) -> Dict[str, str]:
    """Create authentication headers for service requests."""
    headers = {
        "x-internal-id": str(auth.user_id),
        "Content-Type": "application/json",
    }
    
    if auth.service_token:
        headers["Authorization"] = f"Bearer {auth.service_token}"
    
    if auth.internal_id_header:
        headers["x-internal-id"] = auth.internal_id_header
    
    return headers


async def execute_graphql_query(
    client: httpx.AsyncClient,
    config: ServiceConfig,
    auth: AuthContext,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    operation_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a GraphQL query with retry logic and error handling.
    
    Returns the 'data' portion of the GraphQL response or raises an exception.
    """
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    if operation_name:
        payload["operationName"] = operation_name
    
    headers = create_auth_headers(auth)
    
    # First, handle the request without retry for non-retryable errors
    for attempt in range(config.max_retries + 1):
        try:
            response = await client.post(
                f"{config.base_url}/graphql",
                json=payload,
                headers=headers,
                timeout=config.timeout,
            )
            
            # Handle authentication errors immediately (don't retry)
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed", 
                    config.service_name, 
                    response.status_code
                )
            
            # Handle not found errors immediately (don't retry)
            if response.status_code == 404:
                raise DataNotFoundError(
                    "Resource not found", 
                    config.service_name, 
                    response.status_code
                )
            
            # Handle other HTTP errors immediately (don't retry)
            if response.status_code < 500 and not response.is_success:
                raise ServiceClientError(
                    f"Request failed: {response.status_code} - {response.text}",
                    config.service_name,
                    response.status_code,
                )
            
            # Handle 5xx errors - retry these
            if response.status_code >= 500:
                if attempt == config.max_retries:  # Last attempt
                    raise ServiceUnavailableError(
                        f"Service temporarily unavailable: {response.status_code}",
                        config.service_name,
                        response.status_code,
                    )
                else:
                    # Wait before retry (exponential backoff)
                    wait_time = min(4 * (2 ** attempt), 10)  # Exponential backoff capped at 10s
                    await asyncio.sleep(wait_time)
                    continue  # Retry
            
            # Success case - process the response
            result = response.json()
            
            # Handle GraphQL errors in successful HTTP responses
            if "errors" in result:
                error_messages = [err.get("message", "Unknown error") for err in result["errors"]]
                raise ServiceClientError(
                    f"GraphQL errors: {'; '.join(error_messages)}",
                    config.service_name,
                )
            
            return result.get("data", {})
            
        except (AuthenticationError, DataNotFoundError, ServiceClientError) as e:
            # Re-raise these immediately without retry
            raise
        except Exception as e:
            # Handle unexpected errors (connection errors, etc.)
            if attempt == config.max_retries:  # Last attempt
                raise ServiceClientError(
                    f"Unexpected error communicating with {config.service_name}: {str(e)}",
                    config.service_name,
                ) from e
            else:
                # Wait before retry
                wait_time = min(4 * (2 ** attempt), 10)
                await asyncio.sleep(wait_time)
                continue  # Retry
    
    # Should never reach here, but just in case
    raise ServiceUnavailableError(
        f"Service {config.service_name} unavailable after {config.max_retries} attempts",
        config.service_name,
    )


async def execute_rest_request(
    client: httpx.AsyncClient,
    config: ServiceConfig,
    auth: AuthContext,
    method: str,
    path: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a REST API request with retry logic and error handling."""
    headers = create_auth_headers(auth)
    url = f"{config.base_url}{path}"
    
    # Handle the request without retry for non-retryable errors
    for attempt in range(config.max_retries + 1):
        try:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=config.timeout,
            )
            
            # Handle authentication errors immediately (don't retry)
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed", 
                    config.service_name, 
                    response.status_code
                )
            
            # Handle not found errors immediately (don't retry)
            if response.status_code == 404:
                raise DataNotFoundError(
                    "Resource not found", 
                    config.service_name, 
                    response.status_code
                )
            
            # Handle other HTTP errors immediately (don't retry)
            if response.status_code < 500 and not response.is_success:
                raise ServiceClientError(
                    f"Request failed: {response.status_code} - {response.text}",
                    config.service_name,
                    response.status_code,
                )
            
            # Handle 5xx errors - retry these
            if response.status_code >= 500:
                if attempt == config.max_retries:  # Last attempt
                    raise ServiceUnavailableError(
                        f"Service temporarily unavailable: {response.status_code}",
                        config.service_name,
                        response.status_code,
                    )
                else:
                    # Wait before retry (exponential backoff)
                    wait_time = min(4 * (2 ** attempt), 10)  # Exponential backoff capped at 10s
                    await asyncio.sleep(wait_time)
                    continue  # Retry
            
            # Success case
            return response.json()
            
        except (AuthenticationError, DataNotFoundError, ServiceClientError) as e:
            # Re-raise these immediately without retry
            raise
        except Exception as e:
            # Handle unexpected errors (connection errors, etc.)
            if attempt == config.max_retries:  # Last attempt
                raise ServiceClientError(
                    f"Unexpected error communicating with {config.service_name}: {str(e)}",
                    config.service_name,
                ) from e
            else:
                # Wait before retry
                wait_time = min(4 * (2 ** attempt), 10)
                await asyncio.sleep(wait_time)
                continue  # Retry
    
    # Should never reach here, but just in case
    raise ServiceUnavailableError(
        f"Service {config.service_name} unavailable after {config.max_retries} attempts",
        config.service_name,
    )


class BaseServiceClient:
    """
    Base class for service clients with common functionality.
    
    Follows composition over inheritance - provides utilities rather than
    rigid structure.
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising an error if not in async context."""
        if self._client is None:
            raise RuntimeError("Client must be used in async context manager")
        return self._client
    
    async def execute_query(
        self,
        auth: AuthContext,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a GraphQL query."""
        return await execute_graphql_query(
            self.client, self.config, auth, query, variables, operation_name
        )
    
    async def execute_rest(
        self,
        auth: AuthContext,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a REST API request."""
        return await execute_rest_request(
            self.client, self.config, auth, method, path, data, params
        ) 