# Federated Schema Management - Evolution Roadmap

**Status:** Phase 1A (SDL Endpoints) - In Progress
**Owner:** Infrastructure Team
**Updated:** 2025-10-29

## Executive Summary

This document outlines the evolution of MindMirror's GraphQL federated schema management, addressing authentication, VPC networking, and schema change detection challenges.

### Current Architecture

```
Gateway (GraphQL Hive)
├─> mesh-compose: Introspects services at runtime
├─> Builds supergraph from live service schemas
└─> Serves federated GraphQL API
```

**Problem:**
- mesh-compose cannot introspect authenticated endpoints (JWT required)
- Won't work with VPC-isolated services (no public introspection)
- No schema change detection (supergraph only rebuilt on gateway restart)

---

## Phase 1A: Public SDL Endpoints ✅ **IMPLEMENTING NOW**

**Status:** In Progress
**Timeline:** Today (EOD)
**Complexity:** Low

### Objective
Add unauthenticated `/sdl` endpoints to all services so mesh-compose can fetch schemas without authentication.

### Architecture

```
mesh-compose (on gateway startup):
├─> Fetches https://agent-service.../sdl (no auth)
├─> Fetches https://journal-service.../sdl (no auth)
├─> ... all services
└─> Composes supergraph from collected SDLs
```

### Implementation

#### File 1: `src/agent_service/app/main.py` (MODIFY)
**Add SDL endpoint:**

```python
from fastapi.responses import Response

@app.get("/sdl", include_in_schema=False, tags=["internal"])
async def get_schema_sdl():
    """
    Public SDL endpoint for schema composition.
    Returns GraphQL schema in SDL format.
    Used by mesh-compose to build supergraph.

    Note: Exposes schema structure only, not data.
    """
    return Response(
        content=str(schema),  # Strawberry schema object
        media_type="text/plain"
    )
```

**Repeat for:**
- `src/journal_service/journal_service/main.py`
- `habits_service/app/main.py`
- `meals_service/app/main.py`
- `movements_service/app/main.py`
- `practices_service/app/main.py`
- `users_service/app/main.py`

#### File 2: `mesh/entrypoint.sh` (MODIFY)
**Update schema fetching:**

```bash
#!/bin/sh
set -e

echo "Generating mesh config with SDL endpoints..."

# Generate the dynamic mesh config file
echo "import { defineConfig, loadGraphQLHTTPSubgraph } from '@graphql-mesh/compose-cli'

export const composeConfig = defineConfig({
  subgraphs: [
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Journal', {
        endpoint: '${JOURNAL_SERVICE_URL:-http://journal_service:8001}/graphql',
        schemaEndpoint: '${JOURNAL_SERVICE_URL:-http://journal_service:8001}/sdl'
      }),
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Agent', {
        endpoint: '${AGENT_SERVICE_URL:-http://agent_service:8000}/graphql',
        schemaEndpoint: '${AGENT_SERVICE_URL:-http://agent_service:8000}/sdl'
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Habits', {
        endpoint: '${HABITS_SERVICE_URL:-http://habits_service:8003}/graphql',
        schemaEndpoint: '${HABITS_SERVICE_URL:-http://habits_service:8003}/sdl'
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Meals', {
        endpoint: '${MEALS_SERVICE_URL:-http://meals_service:8004}/graphql',
        schemaEndpoint: '${MEALS_SERVICE_URL:-http://meals_service:8004}/sdl'
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Movements', {
        endpoint: '${MOVEMENTS_SERVICE_URL:-http://movements_service:8005}/graphql',
        schemaEndpoint: '${MOVEMENTS_SERVICE_URL:-http://movements_service:8005}/sdl'
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Practices', {
        endpoint: '${PRACTICES_SERVICE_URL:-http://practices_service:8000}/graphql',
        schemaEndpoint: '${PRACTICES_SERVICE_URL:-http://practices_service:8000}/sdl'
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Users', {
        endpoint: '${USERS_SERVICE_URL:-http://users_service:8000}/graphql',
        schemaEndpoint: '${USERS_SERVICE_URL:-http://users_service:8000}/sdl'
      })
    },
  ]
})" > mesh.config.dynamic.ts

exec "$@"
```

### Pros & Cons

**Pros:**
- ✅ Quick implementation (~30 minutes)
- ✅ Works immediately with current architecture
- ✅ mesh-compose can fetch schemas without auth
- ✅ No new infrastructure required

**Cons:**
- ⚠️ Exposes schema structure publicly (structure only, not data)
- ⚠️ Won't work with VPC-isolated services (need Phase 1B)
- ⚠️ Still no schema change detection (need Phase 2)

---

## Phase 1B: Internal Service Account Auth 📋 **NEXT WEEK**

**Status:** Planned
**Timeline:** Next Week
**Complexity:** Medium
**Dependencies:** Phase 1A complete

### Objective
Secure schema introspection with internal service account authentication, enabling VPC support.

### Architecture

```
mesh-compose (with internal JWT):
├─> Fetches https://agent-service.../graphql with MESH_COMPOSE_TOKEN
├─> Service validates internal token
├─> Returns SDL
└─> Composes supergraph securely
```

### Implementation

#### File 1: `src/shared/auth.py` (MODIFY)
**Add internal token validation:**

```python
import os
from typing import Optional
from fastapi import Header, HTTPException

MESH_COMPOSE_TOKEN = os.getenv("MESH_COMPOSE_TOKEN")

class InternalUser:
    """Special user for internal service-to-service communication"""
    id: str = "internal-mesh-compose"
    email: str = "mesh-compose@internal"
    is_internal: bool = True

async def get_current_user_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[User]:
    """
    Validates JWT token or internal mesh-compose token.
    Returns user if valid, None if no token, raises if invalid.
    """
    if not authorization:
        return None

    # Check for internal mesh-compose token first
    if authorization == f"Bearer {MESH_COMPOSE_TOKEN}":
        return InternalUser()

    # Fall through to normal JWT validation
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(
            token,
            key=SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return User(id=payload["sub"], email=payload.get("email"))
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

#### File 2: `mesh/entrypoint.sh` (MODIFY)
**Add auth header for introspection:**

```bash
{
  sourceHandler: loadGraphQLHTTPSubgraph('Agent', {
    endpoint: '${AGENT_SERVICE_URL}/graphql',
    schemaHeaders: {
      'Authorization': 'Bearer ${MESH_COMPOSE_TOKEN}'
    }
  })
}
```

#### File 3: `infra/modules/gateway/main.tf` (MODIFY)
**Add secret for mesh-compose token:**

```hcl
env {
  name = "MESH_COMPOSE_TOKEN"
  value_source {
    secret_key_ref {
      secret  = data.google_secret_manager_secret_version.mesh_compose_token.secret
      version = "latest"
    }
  }
}
```

#### File 4: Service Modules (MODIFY ALL)
**Add mesh-compose token to service env vars:**

```hcl
env {
  name = "MESH_COMPOSE_TOKEN"
  value_source {
    secret_key_ref {
      secret  = data.google_secret_manager_secret_version.mesh_compose_token.secret
      version = "latest"
    }
  }
}
```

#### File 5: Secret Manager Setup
**Create mesh-compose token secret:**

```bash
# Generate secure random token
TOKEN=$(openssl rand -base64 32)

# Create secret in staging
echo "$TOKEN" | gcloud secrets create MESH_COMPOSE_TOKEN \
  --project=mindmirror-69 \
  --data-file=-

# Create secret in production
echo "$TOKEN" | gcloud secrets create MESH_COMPOSE_TOKEN \
  --project=mindmirror-prod \
  --data-file=-
```

### Migration Strategy

1. **Week 1:** Implement internal token validation alongside existing `/sdl` endpoints
2. **Week 2:** Update mesh-compose to use authenticated introspection
3. **Week 3:** Remove public `/sdl` endpoints (optional - can keep for debugging)

### Pros & Cons

**Pros:**
- ✅ Secure - only mesh-compose can introspect schemas
- ✅ Works with VPC (internal Cloud Run to Cloud Run)
- ✅ Preparation for VPC migration
- ✅ Can remove public SDL endpoints

**Cons:**
- ⚠️ Requires secret management across all services
- ⚠️ Adds complexity to auth layer
- ⚠️ Still requires gateway restart for schema changes

---

## Phase 2: Schema Registry with Change Detection 📋 **FUTURE**

**Status:** Documented for Future
**Timeline:** TBD (when Phase 1 becomes bottleneck)
**Complexity:** High
**Dependencies:** Phase 1B complete

### Objective
Automated schema change detection with event-driven gateway redeployment, eliminating manual restarts.

### Architecture

```
Service Startup:
├─> Emits SDL to GCS (gs://mindmirror-schemas/staging/agent.graphql)
└─> Publishes to Pub/Sub: "schema-changed"

Cloud Function (schema-change-detector):
├─> Triggered by Pub/Sub
├─> Compares new SDL hash with cached version
├─> If changed: triggers gateway redeploy
└─> Gateway fetches all SDLs from GCS on startup
```

### Implementation

#### File 1: `src/shared/sdl_emitter.py` (NEW)

```python
"""SDL Emission Utility for Schema Registry"""
import os
from datetime import datetime
from google.cloud import storage
from typing import Optional

def emit_sdl_to_gcs(
    service_name: str,
    sdl_content: str,
    bucket_name: str = "mindmirror-schemas",
    environment: str = "staging"
) -> str:
    """
    Emit GraphQL SDL to GCS for schema registry.

    Args:
        service_name: Name of service (e.g., "agent", "journal")
        sdl_content: GraphQL SDL schema content
        bucket_name: GCS bucket for schemas
        environment: Environment (staging/production)

    Returns:
        GCS path to uploaded schema
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Path: gs://mindmirror-schemas/staging/agent.graphql
    blob_path = f"{environment}/{service_name}.graphql"
    blob = bucket.blob(blob_path)

    # Upload with metadata
    blob.metadata = {
        "service": service_name,
        "environment": environment,
        "timestamp": datetime.utcnow().isoformat()
    }
    blob.upload_from_string(sdl_content, content_type="text/plain")

    print(f"✅ SDL emitted to gs://{bucket_name}/{blob_path}")
    return f"gs://{bucket_name}/{blob_path}"
```

#### File 2: `src/agent_service/app/main.py` (MODIFY)

```python
from shared.sdl_emitter import emit_sdl_to_gcs
import strawberry

@app.on_event("startup")
async def emit_schema():
    """Emit GraphQL schema to GCS on startup"""
    if os.getenv("EMIT_SDL", "true").lower() == "true":
        # Get SDL from Strawberry schema
        sdl = str(schema)

        emit_sdl_to_gcs(
            service_name="agent",
            sdl_content=sdl,
            environment=os.getenv("ENVIRONMENT", "staging")
        )
```

**Repeat for:** journal_service, habits_service, meals_service, movements_service, practices_service, users_service

#### File 3: `mesh/entrypoint.sh` (MAJOR MODIFY)

```bash
#!/bin/sh
set -e

ENVIRONMENT="${ENVIRONMENT:-staging}"
SCHEMA_BUCKET="${SCHEMA_BUCKET:-mindmirror-schemas}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 Fetching Schemas from GCS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Download all service schemas from GCS
mkdir -p /tmp/schemas
for service in agent journal habits meals movements practices users; do
  echo "Fetching ${service}.graphql..."
  gsutil cp "gs://${SCHEMA_BUCKET}/${ENVIRONMENT}/${service}.graphql" "/tmp/schemas/${service}.graphql"
done

echo "✅ All schemas fetched"

# Generate mesh config that loads from local files instead of HTTP
echo "import { defineConfig, loadGraphQLHTTPSubgraph } from '@graphql-mesh/compose-cli'
import { readFileSync } from 'fs'

export const composeConfig = defineConfig({
  subgraphs: [
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Journal', {
        endpoint: '${JOURNAL_SERVICE_URL}/graphql',
        // Use pre-fetched schema instead of introspection
        schema: readFileSync('/tmp/schemas/journal.graphql', 'utf-8')
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Agent', {
        endpoint: '${AGENT_SERVICE_URL}/graphql',
        schema: readFileSync('/tmp/schemas/agent.graphql', 'utf-8')
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Habits', {
        endpoint: '${HABITS_SERVICE_URL}/graphql',
        schema: readFileSync('/tmp/schemas/habits.graphql', 'utf-8')
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Meals', {
        endpoint: '${MEALS_SERVICE_URL}/graphql',
        schema: readFileSync('/tmp/schemas/meals.graphql', 'utf-8')
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Movements', {
        endpoint: '${MOVEMENTS_SERVICE_URL}/graphql',
        schema: readFileSync('/tmp/schemas/movements.graphql', 'utf-8')
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Practices', {
        endpoint: '${PRACTICES_SERVICE_URL}/graphql',
        schema: readFileSync('/tmp/schemas/practices.graphql', 'utf-8')
      })
    },
    {
      sourceHandler: loadGraphQLHTTPSubgraph('Users', {
        endpoint: '${USERS_SERVICE_URL}/graphql',
        schema: readFileSync('/tmp/schemas/users.graphql', 'utf-8')
      })
    },
  ]
})" > mesh.config.dynamic.ts

echo "✅ Mesh config generated with GCS schemas"

exec "$@"
```

#### File 4: `infra-v2/functions/schema-change-detector/main.py` (NEW)

```python
"""Schema Change Detection Function"""
import os
from google.cloud import run_v2
from google.cloud import storage
import hashlib
import json
from flask import Request

def schema_changed(request: Request):
    """
    Triggered by Pub/Sub when a service emits new SDL.
    Compares with cached version and triggers gateway redeploy if changed.
    """
    # Parse Pub/Sub message
    envelope = request.get_json()
    payload = envelope['message']['data']

    service_name = payload['service']
    environment = payload['environment']

    # Fetch new schema
    client = storage.Client()
    bucket = client.bucket("mindmirror-schemas")
    blob = bucket.blob(f"{environment}/{service_name}.graphql")
    new_schema = blob.download_as_text()

    # Compare with cached hash
    cache_blob = bucket.blob(f"{environment}/.cache/{service_name}.hash")
    try:
        old_hash = cache_blob.download_as_text()
    except:
        old_hash = None

    new_hash = hashlib.sha256(new_schema.encode()).hexdigest()

    if old_hash != new_hash:
        print(f"🔄 Schema changed for {service_name}, triggering gateway redeploy")

        # Update cache
        cache_blob.upload_from_string(new_hash)

        # Trigger gateway redeploy
        project_id = os.getenv("GCP_PROJECT_ID")
        region = os.getenv("GCP_REGION")
        gateway_service = f"gateway-{environment}" if environment == "staging" else "gateway"

        run_client = run_v2.ServicesClient()
        service_path = run_client.service_path(project_id, region, gateway_service)

        # Trigger new revision by updating env var
        operation = run_client.update_service(
            request={
                "service": {
                    "name": service_path,
                    "template": {
                        "containers": [{
                            "env": [{
                                "name": "SCHEMA_VERSION",
                                "value": new_hash[:8]
                            }]
                        }]
                    }
                }
            }
        )

        print(f"✅ Gateway redeploy triggered")
    else:
        print(f"✨ No schema changes for {service_name}")

    return {"status": "ok"}
```

#### File 5: `infra-v2/modules/schema-registry/main.tf` (NEW)

```hcl
# GCS bucket for schemas
resource "google_storage_bucket" "schemas" {
  name     = "mindmirror-schemas"
  location = var.region
  project  = var.project_id

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      num_newer_versions = 10
    }
    action {
      type = "Delete"
    }
  }

  versioning {
    enabled = true
  }
}

# Pub/Sub topic for schema changes
resource "google_pubsub_topic" "schema_changes" {
  name    = "schema-changes-${var.environment}"
  project = var.project_id
}

# Cloud Function for schema change detection
resource "google_cloudfunctions2_function" "schema_detector" {
  name     = "schema-change-detector-${var.environment}"
  location = var.region
  project  = var.project_id

  build_config {
    runtime     = "python311"
    entry_point = "schema_changed"
    source {
      storage_source {
        bucket = google_storage_bucket.function_code.name
        object = google_storage_bucket_object.function_code.name
      }
    }
  }

  service_config {
    available_memory = "256M"
    timeout_seconds  = 60

    environment_variables = {
      GCP_PROJECT_ID = var.project_id
      GCP_REGION     = var.region
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.schema_changes.id
  }
}
```

#### File 6: `.github/workflows/deploy-to-staging.yml` (MODIFY)

```yaml
- name: Trigger Schema Emission
  run: |
    # Publish to Pub/Sub to trigger schema change detection
    gcloud pubsub topics publish schema-changes-staging \
      --project=${{ env.GCP_PROJECT_ID }} \
      --message='{"service":"agent","environment":"staging"}'
```

### Pros & Cons

**Pros:**
- ✅ Automatic schema change detection
- ✅ Gateway only redeploys when schemas actually change
- ✅ Schema history/versioning in GCS
- ✅ Offline schema access (cached)
- ✅ Decouples schema from service availability

**Cons:**
- ⚠️ High complexity (~20+ files changed)
- ⚠️ New infrastructure (GCS, Pub/Sub, Cloud Function)
- ⚠️ Moderate operational overhead
- ⚠️ 1-2 day implementation timeline

---

## Comparison Matrix

| Aspect                | Phase 1A (SDL)     | Phase 1B (Auth)        | Phase 2 (Registry)         |
|-----------------------|--------------------|------------------------|----------------------------|
| **Complexity**        | Low                | Medium                 | High                       |
| **Files Changed**     | ~8                 | ~15                    | ~25+                       |
| **New Infrastructure**| None               | Secret only            | GCS + Pub/Sub + Function   |
| **Auth Security**     | None (public SDL)  | Internal token         | Internal token             |
| **VPC Support**       | No                 | Yes                    | Yes                        |
| **Change Detection**  | Manual restart     | Manual restart         | Automatic                  |
| **Schema History**    | No                 | No                     | Yes (GCS versioning)       |
| **Implementation**    | 30 minutes         | 4-6 hours              | 1-2 days                   |
| **Maintenance**       | Minimal            | Low                    | Moderate                   |

---

## Decision Triggers

### When to Move to Phase 1B
- ✅ VPC migration timeline confirmed
- ✅ Security audit requires schema introspection auth
- ✅ Public SDL exposure becomes compliance issue

### When to Move to Phase 2
- ✅ Gateway redeploys failing frequently (>5% failure rate)
- ✅ Schema changes happening >10x per day
- ✅ Need schema rollback capability
- ✅ Multiple environments with divergent schemas
- ✅ Gateway restart time >2 minutes

---

## Current Status

**Phase 1A:** ✅ Implementing today
**Phase 1B:** 📋 Documented, scheduled for next week
**Phase 2:** 📋 Documented, evaluate after Phase 1B complete

**Next Steps:**
1. Complete Phase 1A implementation (today)
2. Test staging deployment with SDL endpoints
3. Verify Vercel cutover functionality
4. Schedule Phase 1B for next week
5. Re-evaluate Phase 2 necessity in 2-4 weeks
