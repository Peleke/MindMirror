# EPIC: HMAC Service-to-Service Authentication

**Status**: Planning
**Priority**: High (Post-MVP)
**Estimated Effort**: 2-3 weeks
**Dependencies**: None (can be implemented independently)

---

## Overview

Implement pairwise HMAC-based authentication for all service-to-service communication in MindMirror. Replace the current `x-internal-id` header-only approach with cryptographically signed requests to prevent service impersonation, replay attacks, and unauthorized internal API access.

**Security Goals:**
1. **Mutual Authentication**: Services verify each other's identity
2. **Request Integrity**: Tampered requests are detected and rejected
3. **Replay Prevention**: Requests can't be captured and replayed
4. **Key Rotation**: Support key rotation without downtime
5. **Auditability**: Log all authentication attempts for security monitoring

---

## Current State Analysis

### Current Authentication Pattern

From `src/shared/clients/base.py`:

```python
def create_auth_headers(auth: AuthContext) -> Dict[str, str]:
    headers = {
        "x-internal-id": str(auth.user_id),  # Plain user ID - no verification!
        "Content-Type": "application/json",
    }

    if auth.service_token:
        headers["Authorization"] = f"Bearer {auth.service_token}"  # Not implemented

    return headers
```

### Security Gaps

1. **No Request Signing**: Any service can set `x-internal-id` to any value
2. **No Sender Verification**: Recipient can't verify who sent the request
3. **No Tamper Detection**: Request body can be modified in transit
4. **No Replay Protection**: Captured requests can be replayed indefinitely
5. **No Key Management**: No infrastructure for rotating credentials

### Threat Model

**Threats Mitigated:**
- **Service Impersonation**: Malicious service pretends to be trusted service
- **User Impersonation**: Service sets `x-internal-id` to another user's ID
- **Man-in-the-Middle**: Attacker intercepts and modifies requests
- **Replay Attacks**: Attacker captures and replays valid requests
- **Internal API Abuse**: Compromised service makes unauthorized calls

**Threats NOT Mitigated (out of scope):**
- TLS/SSL layer attacks (assumes HTTPS)
- Container/host compromise (assumes secure infrastructure)
- Credential theft from secrets storage (assumes secure secrets management)

---

## Architecture Design

### HMAC Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Service A (Client)                            │
│                                                                 │
│  1. Prepare request payload                                    │
│  2. Generate signature:                                        │
│     - timestamp = current_unix_time()                          │
│     - message = "timestamp.service_a.service_b.method.path.body"│
│     - signature = HMAC-SHA256(message, shared_secret)         │
│  3. Add headers:                                               │
│     - X-Service-Name: "service_a"                             │
│     - X-Service-Timestamp: timestamp                          │
│     - X-Service-Signature: signature                          │
│     - X-User-ID: user_id (if applicable)                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS Request
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Service B (Server)                            │
│                                                                 │
│  4. Receive request                                            │
│  5. Extract headers:                                           │
│     - sender = X-Service-Name                                 │
│     - timestamp = X-Service-Timestamp                         │
│     - signature = X-Service-Signature                         │
│  6. Validate request:                                          │
│     ✓ Check sender is allowed                                 │
│     ✓ Check timestamp freshness (< 5 min old)                │
│     ✓ Reconstruct message from request                        │
│     ✓ Compute expected signature with shared secret           │
│     ✓ Compare signatures (constant-time comparison)           │
│  7. If valid:                                                  │
│     - Process request                                          │
│     - Return response                                          │
│     Else:                                                       │
│     - Log authentication failure                               │
│     - Return 401 Unauthorized                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Signature Generation Algorithm

```python
def generate_hmac_signature(
    sender: str,
    receiver: str,
    method: str,
    path: str,
    body: Optional[str],
    secret: bytes,
    timestamp: Optional[int] = None
) -> Tuple[str, int]:
    """
    Generate HMAC-SHA256 signature for service-to-service request.

    Returns:
        (signature, timestamp) tuple
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Canonical message format
    # This must match exactly on both sender and receiver
    message_parts = [
        str(timestamp),
        sender,
        receiver,
        method.upper(),
        path,
        body or "",
    ]
    message = ".".join(message_parts)

    # Generate signature
    signature = hmac.new(
        key=secret,
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    return signature, timestamp
```

### Signature Verification Algorithm

```python
def verify_hmac_signature(
    sender: str,
    receiver: str,
    method: str,
    path: str,
    body: Optional[str],
    signature: str,
    timestamp: int,
    secret: bytes,
    max_age_seconds: int = 300  # 5 minutes
) -> bool:
    """
    Verify HMAC-SHA256 signature from service request.

    Returns:
        True if signature is valid and fresh, False otherwise
    """
    # 1. Check timestamp freshness (prevent replay attacks)
    current_time = int(time.time())
    age = current_time - timestamp

    if age < 0 or age > max_age_seconds:
        logger.warning(
            f"Request timestamp out of range: age={age}s, max={max_age_seconds}s"
        )
        return False

    # 2. Reconstruct message using same format as sender
    message_parts = [
        str(timestamp),
        sender,
        receiver,
        method.upper(),
        path,
        body or "",
    ]
    message = ".".join(message_parts)

    # 3. Compute expected signature
    expected_signature = hmac.new(
        key=secret,
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    # 4. Constant-time comparison (prevent timing attacks)
    return hmac.compare_digest(signature, expected_signature)
```

---

## Implementation Plan

### Phase 1: Infrastructure (Week 1)

**1.1: Secret Management Setup**

Create pairwise shared secrets for all service pairs:

```
Service Pairs (bidirectional):
- agent_service ↔ practices_service
- agent_service ↔ meals_service
- agent_service ↔ users_service
- journal_service ↔ agent_service (existing)
- practices_service ↔ users_service
- meals_service ↔ users_service
- ... (all combinations)
```

**Secret Storage Options:**

**Option A: Environment Variables (simplest for local)**
```bash
# .env
HMAC_SECRET_AGENT_PRACTICES=base64-encoded-secret
HMAC_SECRET_AGENT_MEALS=base64-encoded-secret
HMAC_SECRET_JOURNAL_AGENT=base64-encoded-secret
# ... etc
```

**Option B: Google Secret Manager (production)**
```python
# Secrets stored as:
# projects/mindmirror-prod/secrets/hmac-agent-practices/versions/latest
# projects/mindmirror-prod/secrets/hmac-agent-meals/versions/latest

from shared.secrets import get_secret

secret = get_secret(
    f"hmac-{sender_service}-{receiver_service}",
    project_id="mindmirror-prod"
)
```

**Option C: HashiCorp Vault (enterprise)**
```python
# vault kv get secret/hmac/agent-practices
# vault kv get secret/hmac/agent-meals

import hvac

client = hvac.Client(url="http://vault:8200")
secret = client.secrets.kv.v2.read_secret_version(
    path=f"hmac/{sender_service}-{receiver_service}"
)
```

**Recommendation:** Start with **Option A** (env vars) for local, migrate to **Option B** (Secret Manager) for production.

**1.2: Secret Generation Utility**

```python
# scripts/generate_hmac_secrets.py
import secrets
import base64

def generate_service_secrets(services: list[str]) -> dict[str, str]:
    """Generate pairwise HMAC secrets for all service combinations"""
    service_secrets = {}

    for i, sender in enumerate(services):
        for receiver in services[i+1:]:
            # Generate cryptographically secure random secret (32 bytes)
            secret = secrets.token_bytes(32)
            secret_b64 = base64.b64encode(secret).decode("utf-8")

            # Store with canonical naming (alphabetical)
            pair = tuple(sorted([sender, receiver]))
            key = f"HMAC_SECRET_{pair[0].upper()}_{pair[1].upper()}"
            service_secrets[key] = secret_b64

    return service_secrets

services = [
    "agent",
    "journal",
    "practices",
    "meals",
    "movements",
    "habits",
    "users",
]

secrets = generate_service_secrets(services)

# Output for .env
for key, value in secrets.items():
    print(f"{key}={value}")
```

**1.3: Secrets Access Layer**

```python
# src/shared/shared/hmac_secrets.py
import base64
import os
from typing import Optional
from functools import lru_cache

class HMACSecretManager:
    """Manage HMAC secrets for service-to-service auth"""

    def __init__(self, secret_backend: str = "env"):
        self.backend = secret_backend

    @lru_cache(maxsize=100)
    def get_secret(self, sender: str, receiver: str) -> bytes:
        """
        Get shared secret for service pair.

        Secrets are bidirectional - get_secret("a", "b") == get_secret("b", "a")
        """
        # Canonical naming (alphabetical)
        pair = tuple(sorted([sender, receiver]))
        key = f"HMAC_SECRET_{pair[0].upper()}_{pair[1].upper()}"

        if self.backend == "env":
            return self._get_from_env(key)
        elif self.backend == "gcp":
            return self._get_from_gcp_secret_manager(key)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _get_from_env(self, key: str) -> bytes:
        """Get secret from environment variable"""
        secret_b64 = os.getenv(key)
        if not secret_b64:
            raise ValueError(f"HMAC secret not found: {key}")

        return base64.b64decode(secret_b64)

    def _get_from_gcp_secret_manager(self, key: str) -> bytes:
        """Get secret from Google Secret Manager"""
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GCP_PROJECT_ID", "mindmirror-prod")

        name = f"projects/{project_id}/secrets/{key.lower()}/versions/latest"
        response = client.access_secret_version(request={"name": name})

        return response.payload.data

# Global instance
secret_manager = HMACSecretManager(
    secret_backend=os.getenv("HMAC_SECRET_BACKEND", "env")
)
```

### Phase 2: Core Authentication Library (Week 1-2)

**2.1: HMAC Signing Module**

```python
# src/shared/shared/hmac_auth.py
import hmac
import hashlib
import time
from typing import Optional, Tuple
from dataclasses import dataclass

from .hmac_secrets import secret_manager

@dataclass
class ServiceAuthHeaders:
    """Headers for HMAC-authenticated service request"""
    service_name: str
    timestamp: int
    signature: str
    user_id: Optional[str] = None

def sign_service_request(
    sender: str,
    receiver: str,
    method: str,
    path: str,
    body: Optional[str] = None,
    user_id: Optional[str] = None,
    timestamp: Optional[int] = None
) -> ServiceAuthHeaders:
    """
    Sign a service-to-service request with HMAC-SHA256.

    Args:
        sender: Name of sending service (e.g., "agent_service")
        receiver: Name of receiving service (e.g., "practices_service")
        method: HTTP method (GET, POST, etc.)
        path: Request path (e.g., "/graphql")
        body: Request body (JSON string or None)
        user_id: User ID if request is on behalf of user
        timestamp: Unix timestamp (defaults to current time)

    Returns:
        ServiceAuthHeaders with signature and metadata
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Get shared secret for this service pair
    secret = secret_manager.get_secret(sender, receiver)

    # Build canonical message
    message_parts = [
        str(timestamp),
        sender,
        receiver,
        method.upper(),
        path,
        body or "",
    ]
    message = ".".join(message_parts)

    # Generate signature
    signature = hmac.new(
        key=secret,
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    return ServiceAuthHeaders(
        service_name=sender,
        timestamp=timestamp,
        signature=signature,
        user_id=user_id
    )

def verify_service_request(
    sender: str,
    receiver: str,
    method: str,
    path: str,
    body: Optional[str],
    signature: str,
    timestamp: int,
    max_age_seconds: int = 300
) -> bool:
    """
    Verify HMAC signature from service request.

    Args:
        sender: Name of sending service from X-Service-Name header
        receiver: Name of this service (receiving)
        method: HTTP method from request
        path: Request path from request
        body: Request body (JSON string or None)
        signature: Signature from X-Service-Signature header
        timestamp: Timestamp from X-Service-Timestamp header
        max_age_seconds: Maximum allowed age (default 5 minutes)

    Returns:
        True if signature is valid and fresh
    """
    # 1. Check timestamp freshness
    current_time = int(time.time())
    age = current_time - timestamp

    if age < 0:
        # Timestamp in the future (clock skew or attack)
        return False

    if age > max_age_seconds:
        # Request too old (replay attack or network delay)
        return False

    # 2. Get shared secret
    try:
        secret = secret_manager.get_secret(sender, receiver)
    except ValueError:
        # No secret configured for this service pair
        return False

    # 3. Reconstruct message
    message_parts = [
        str(timestamp),
        sender,
        receiver,
        method.upper(),
        path,
        body or "",
    ]
    message = ".".join(message_parts)

    # 4. Compute expected signature
    expected_signature = hmac.new(
        key=secret,
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    # 5. Constant-time comparison
    return hmac.compare_digest(signature, expected_signature)
```

**2.2: FastAPI Middleware**

```python
# src/shared/shared/hmac_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from .hmac_auth import verify_service_request

logger = logging.getLogger(__name__)

class HMACAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify HMAC signatures on incoming service requests.
    """

    def __init__(self, app, service_name: str, exempt_paths: list[str] = None):
        super().__init__(app)
        self.service_name = service_name
        self.exempt_paths = exempt_paths or ["/health", "/metrics"]

    async def dispatch(self, request: Request, call_next):
        # Skip HMAC check for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Extract auth headers
        sender = request.headers.get("X-Service-Name")
        timestamp_str = request.headers.get("X-Service-Timestamp")
        signature = request.headers.get("X-Service-Signature")

        if not all([sender, timestamp_str, signature]):
            logger.warning(
                f"Missing HMAC headers from {request.client.host}: "
                f"sender={sender}, timestamp={timestamp_str}, signature={signature}"
            )
            raise HTTPException(
                status_code=401,
                detail="Missing service authentication headers"
            )

        try:
            timestamp = int(timestamp_str)
        except ValueError:
            logger.warning(f"Invalid timestamp from {sender}: {timestamp_str}")
            raise HTTPException(
                status_code=401,
                detail="Invalid timestamp format"
            )

        # Read body for signature verification
        body = await request.body()
        body_str = body.decode("utf-8") if body else None

        # Verify signature
        is_valid = verify_service_request(
            sender=sender,
            receiver=self.service_name,
            method=request.method,
            path=request.url.path,
            body=body_str,
            signature=signature,
            timestamp=timestamp
        )

        if not is_valid:
            logger.warning(
                f"Invalid HMAC signature from {sender} to {self.service_name}: "
                f"method={request.method}, path={request.url.path}"
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid service authentication signature"
            )

        # Attach authenticated service name to request state
        request.state.authenticated_service = sender
        request.state.user_id = request.headers.get("X-User-ID")

        logger.info(
            f"Authenticated service request: {sender} → {self.service_name} "
            f"({request.method} {request.url.path})"
        )

        return await call_next(request)
```

**2.3: Updated Base Client**

```python
# src/shared/clients/base.py (updated)
from shared.hmac_auth import sign_service_request, ServiceAuthHeaders

def create_auth_headers_hmac(
    sender: str,
    receiver: str,
    method: str,
    path: str,
    body: Optional[str],
    auth: AuthContext
) -> Dict[str, str]:
    """Create HMAC-authenticated headers for service request"""

    # Sign the request
    auth_headers = sign_service_request(
        sender=sender,
        receiver=receiver,
        method=method,
        path=path,
        body=body,
        user_id=str(auth.user_id) if auth.user_id else None
    )

    # Build headers
    headers = {
        "Content-Type": "application/json",
        "X-Service-Name": auth_headers.service_name,
        "X-Service-Timestamp": str(auth_headers.timestamp),
        "X-Service-Signature": auth_headers.signature,
    }

    if auth_headers.user_id:
        headers["X-User-ID"] = auth_headers.user_id

    return headers

# Update execute_graphql_query to use HMAC
async def execute_graphql_query(
    client: httpx.AsyncClient,
    config: ServiceConfig,
    auth: AuthContext,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    operation_name: Optional[str] = None,
    sender_service: str = "unknown",  # NEW: caller must provide
) -> Dict[str, Any]:
    """Execute GraphQL query with HMAC authentication"""

    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    if operation_name:
        payload["operationName"] = operation_name

    body = json.dumps(payload)
    path = "/graphql"

    # Create HMAC-authenticated headers
    headers = create_auth_headers_hmac(
        sender=sender_service,
        receiver=config.service_name,
        method="POST",
        path=path,
        body=body,
        auth=auth
    )

    # ... rest of implementation
```

### Phase 3: Service Integration (Week 2)

**3.1: Update Each Service**

For each service (`agent_service`, `practices_service`, `meals_service`, etc.):

```python
# src/{service}/app/main.py
from fastapi import FastAPI
from shared.hmac_middleware import HMACAuthMiddleware

app = FastAPI()

# Add HMAC middleware
app.add_middleware(
    HMACAuthMiddleware,
    service_name="practices_service",  # Service's own name
    exempt_paths=["/health", "/metrics", "/graphql"]  # Public endpoints
)
```

**3.2: Update Service Clients**

```python
# src/agent_service/app/clients/practices_client.py
class PracticesServiceClient(BaseServiceClient):
    def __init__(self, config: ServiceConfig, sender_service: str = "agent_service"):
        super().__init__(config)
        self.sender_service = sender_service

    async def create_practice_template(
        self,
        auth: AuthContext,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        mutation = """..."""

        result = await self.execute_query(
            auth=auth,
            query=mutation,
            variables={"input": template_data},
            operation_name="CreatePracticeTemplate",
            sender_service=self.sender_service  # Pass sender identity
        )

        return result["createPracticeTemplate"]
```

### Phase 4: Testing & Validation (Week 3)

**4.1: Unit Tests**

```python
# tests/test_hmac_auth.py
import pytest
import time
from shared.hmac_auth import sign_service_request, verify_service_request
from shared.hmac_secrets import HMACSecretManager

@pytest.fixture
def secret_manager(monkeypatch):
    """Mock secret manager with test secret"""
    monkeypatch.setenv(
        "HMAC_SECRET_AGENT_PRACTICES",
        "dGVzdC1zZWNyZXQtMzItYnl0ZXMtbG9uZy1mb3ItdGVzdGluZw=="
    )
    return HMACSecretManager(secret_backend="env")

def test_sign_and_verify_valid_request(secret_manager):
    """Test that valid signature is verified"""
    sender = "agent"
    receiver = "practices"
    method = "POST"
    path = "/graphql"
    body = '{"query": "..."}'

    # Sign request
    auth_headers = sign_service_request(
        sender=sender,
        receiver=receiver,
        method=method,
        path=path,
        body=body
    )

    # Verify signature
    is_valid = verify_service_request(
        sender=sender,
        receiver=receiver,
        method=method,
        path=path,
        body=body,
        signature=auth_headers.signature,
        timestamp=auth_headers.timestamp
    )

    assert is_valid

def test_verify_rejects_tampered_body(secret_manager):
    """Test that tampered body fails verification"""
    sender = "agent"
    receiver = "practices"
    method = "POST"
    path = "/graphql"
    body = '{"query": "..."}'

    # Sign request
    auth_headers = sign_service_request(
        sender=sender,
        receiver=receiver,
        method=method,
        path=path,
        body=body
    )

    # Tamper with body
    tampered_body = '{"query": "MALICIOUS"}'

    # Verification should fail
    is_valid = verify_service_request(
        sender=sender,
        receiver=receiver,
        method=method,
        path=path,
        body=tampered_body,
        signature=auth_headers.signature,
        timestamp=auth_headers.timestamp
    )

    assert not is_valid

def test_verify_rejects_expired_timestamp(secret_manager):
    """Test that old requests are rejected"""
    sender = "agent"
    receiver = "practices"
    method = "POST"
    path = "/graphql"
    body = '{"query": "..."}'

    # Sign request with old timestamp (10 minutes ago)
    old_timestamp = int(time.time()) - 600
    auth_headers = sign_service_request(
        sender=sender,
        receiver=receiver,
        method=method,
        path=path,
        body=body,
        timestamp=old_timestamp
    )

    # Verification should fail (max age is 5 minutes)
    is_valid = verify_service_request(
        sender=sender,
        receiver=receiver,
        method=method,
        path=path,
        body=body,
        signature=auth_headers.signature,
        timestamp=auth_headers.timestamp,
        max_age_seconds=300
    )

    assert not is_valid

def test_verify_rejects_wrong_service_pair(secret_manager):
    """Test that signature from wrong service pair fails"""
    # Sign as agent → practices
    auth_headers = sign_service_request(
        sender="agent",
        receiver="practices",
        method="POST",
        path="/graphql",
        body='{"query": "..."}'
    )

    # Try to verify as agent → meals (wrong pair)
    is_valid = verify_service_request(
        sender="agent",
        receiver="meals",  # Wrong receiver!
        method="POST",
        path="/graphql",
        body='{"query": "..."}',
        signature=auth_headers.signature,
        timestamp=auth_headers.timestamp
    )

    assert not is_valid
```

**4.2: Integration Tests**

```python
# tests/integration/test_hmac_service_calls.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_practices_service_accepts_valid_hmac():
    """Test that practices_service accepts valid HMAC request"""
    async with AsyncClient(base_url="http://practices_service:8006") as client:
        from shared.hmac_auth import sign_service_request

        body = '{"query": "{ __typename }"}'
        auth_headers = sign_service_request(
            sender="agent",
            receiver="practices",
            method="POST",
            path="/graphql",
            body=body
        )

        headers = {
            "Content-Type": "application/json",
            "X-Service-Name": auth_headers.service_name,
            "X-Service-Timestamp": str(auth_headers.timestamp),
            "X-Service-Signature": auth_headers.signature,
        }

        response = await client.post("/graphql", content=body, headers=headers)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_practices_service_rejects_invalid_signature():
    """Test that practices_service rejects invalid HMAC request"""
    async with AsyncClient(base_url="http://practices_service:8006") as client:
        headers = {
            "Content-Type": "application/json",
            "X-Service-Name": "agent",
            "X-Service-Timestamp": str(int(time.time())),
            "X-Service-Signature": "invalid-signature-here",
        }

        body = '{"query": "{ __typename }"}'
        response = await client.post("/graphql", content=body, headers=headers)
        assert response.status_code == 401
```

**4.3: End-to-End Tests**

Test full workflow with HMAC enabled:
1. Agent service receives user request
2. Agent service calls practices_service with HMAC
3. Practices_service verifies HMAC and processes request
4. Response flows back successfully

### Phase 5: Deployment & Migration (Week 3)

**5.1: Rollout Strategy**

**Phase 5.1.1: Generate Secrets**
```bash
# Generate all service secrets
python scripts/generate_hmac_secrets.py > .env.hmac

# Upload to Secret Manager (production)
./scripts/upload_secrets_to_gcp.sh
```

**Phase 5.1.2: Backward-Compatible Mode**

Add feature flag to support both old and new auth:

```python
# Environment variable
HMAC_AUTH_ENABLED=false  # Start disabled

# Middleware with fallback
class HMACAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str, enforce: bool = False):
        super().__init__(app)
        self.service_name = service_name
        self.enforce = enforce  # If False, log but don't reject

    async def dispatch(self, request: Request, call_next):
        # Check for HMAC headers
        has_hmac = all([
            request.headers.get("X-Service-Name"),
            request.headers.get("X-Service-Timestamp"),
            request.headers.get("X-Service-Signature"),
        ])

        if has_hmac:
            # Verify HMAC
            is_valid = verify_service_request(...)

            if not is_valid:
                if self.enforce:
                    raise HTTPException(status_code=401)
                else:
                    logger.warning("Invalid HMAC (not enforced)")
        else:
            # No HMAC headers
            if self.enforce:
                raise HTTPException(status_code=401, detail="HMAC required")
            else:
                logger.info("No HMAC headers (not enforced)")

        return await call_next(request)
```

**Phase 5.1.3: Gradual Rollout**

1. **Week 1**: Deploy middleware in non-enforcing mode (logs only)
2. **Week 2**: Update clients to send HMAC headers
3. **Week 3**: Monitor logs for 100% HMAC coverage
4. **Week 4**: Enable enforcement (`HMAC_AUTH_ENABLED=true`)

**5.2: Monitoring & Alerting**

```python
# Metrics to track
- hmac_auth_success_total (counter)
- hmac_auth_failure_total (counter)
- hmac_auth_latency_seconds (histogram)
- hmac_auth_timestamp_age_seconds (histogram)

# Alerts
- Alert if hmac_auth_failure_total > 10/min (possible attack)
- Alert if hmac_auth_timestamp_age_seconds > 60s (clock skew)
```

---

## Key Rotation Strategy

### Rotation Process

```python
# 1. Generate new secret
new_secret = secrets.token_bytes(32)

# 2. Store with version suffix
# Old: HMAC_SECRET_AGENT_PRACTICES
# New: HMAC_SECRET_AGENT_PRACTICES_V2

# 3. Update secret manager to check both versions
def get_secret(self, sender: str, receiver: str, version: int = None) -> bytes:
    if version:
        key = f"{base_key}_V{version}"
    else:
        # Try V2 first, fallback to V1
        try:
            return self._get_secret(f"{base_key}_V2")
        except:
            return self._get_secret(base_key)

# 4. Deploy updated services (accept both V1 and V2)
# 5. Update clients to send V2
# 6. Remove V1 secrets after grace period
```

### Rotation Schedule

- **Production**: Rotate every 90 days
- **Staging**: Rotate every 30 days (test rotation process)
- **Local/Dev**: No rotation (use static test secrets)

---

## Success Metrics

### Security Metrics

- **Zero** successful service impersonation attacks
- **Zero** successful replay attacks
- **<0.1%** false positive rate (valid requests rejected)
- **100%** secret rotation success rate

### Performance Metrics

- **<1ms** signature generation latency (p95)
- **<1ms** signature verification latency (p95)
- **<5%** overhead vs non-HMAC requests

### Operational Metrics

- **100%** HMAC coverage (all service calls signed)
- **Zero** authentication-related downtime
- **<10** manual interventions per quarter

---

## Acceptance Criteria

- [ ] All service pairs have generated secrets
- [ ] Secrets stored securely (env vars locally, Secret Manager in prod)
- [ ] HMAC signing implemented in `shared.hmac_auth`
- [ ] HMAC middleware implemented and tested
- [ ] All service clients updated to send HMAC headers
- [ ] All services updated with HMAC middleware
- [ ] Backward compatibility mode works (logs warnings)
- [ ] Enforcement mode works (rejects invalid signatures)
- [ ] Unit tests: 95%+ coverage
- [ ] Integration tests: all service pairs tested
- [ ] E2E tests: full workflows with HMAC enabled
- [ ] Documentation: architecture, rollout plan, key rotation
- [ ] Monitoring: dashboards and alerts configured
- [ ] Rollout: deployed to staging successfully
- [ ] Rollout: deployed to production successfully
- [ ] Post-deployment: zero auth-related incidents for 30 days

---

## Rollback Plan

If issues arise during rollout:

1. **Immediate**: Set `HMAC_AUTH_ENABLED=false` on all services (falls back to old auth)
2. **Investigation**: Review logs to identify root cause
3. **Fix**: Patch issue in staging
4. **Retry**: Re-enable HMAC after validation

---

## Related Work

- [EPIC: Agent Service Implementation](./EPIC_Agent_Service_Implementation.md) - Uses HMAC for service calls
- Future: Rotate secrets automatically via cron job
- Future: Mutual TLS (mTLS) for defense in depth
- Future: Zero-trust networking with service mesh

---

## References

- [RFC 2104: HMAC Specification](https://www.rfc-editor.org/rfc/rfc2104)
- [OWASP: API Security](https://owasp.org/www-project-api-security/)
- [Google Cloud Secret Manager Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)
