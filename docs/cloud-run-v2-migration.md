# Cloud Run v1 → v2 Migration Guide

**Goal**: Migrate all services from legacy Cloud Run v1 to Cloud Run v2
**Why**: v2 provides VPC networking, secret volumes, better performance, and modern features
**Timeline**: 1-2 weeks (one service per day approach)

---

## Why Migrate to Cloud Run v2?

### Features Available Only in v2
| Feature | v1 | v2 | Benefit |
|---------|----|----|---------|
| **VPC Direct** | ❌ | ✅ | Private IPs, no Serverless Connector needed |
| **Secret Volumes** | ❌ | ✅ | Mount secrets as files (more secure) |
| **Execution Environment** | gen1 | gen2 | Faster cold starts, more memory |
| **Startup/Liveness Probes** | Limited | Native | Better health checks |
| **Multi-Container Support** | ❌ | ✅ | Sidecars (e.g., Cloud SQL Proxy) |
| **Direct VPC Egress** | Via Connector | Direct | Simpler networking, lower cost |
| **Service Mesh Integration** | ❌ | ✅ | Istio/Anthos support |
| **gRPC Streaming** | Limited | Full | Bidirectional streaming |

### Why This Matters for MindMirror
- **VPC Networking**: Backend services can communicate internally (not over public internet)
- **Secret Volumes**: Database passwords, API keys not visible in Cloud Console
- **Performance**: Faster cold starts for AI/embedding services (agent_service)
- **Security**: Internal ingress (no public endpoints for backend services)

---

## Migration Strategy

### Approach: One Service at a Time
**Rationale**: Minimize risk, validate each migration before proceeding

**Order** (low-risk → high-risk):
1. ✅ **Pilot**: practices_service (simple, low traffic, easy rollback)
2. movements_service (simple, isolated database)
3. users_service (simple, low traffic)
4. meals_service (simple, external API calls)
5. habits_service (medium complexity, shared database)
6. journal_service (medium complexity, shared database, Celery integration)
7. celery_worker_web (background tasks, Pub/Sub integration)
8. agent_service (complex, AI/embeddings, high traffic)
9. gateway (critical path, last to migrate)

**Timeline**: 1 service per day = 9 days total

---

## Breaking Changes

### Resource Type Change
```hcl
# Before (v1)
resource "google_cloud_run_service" "agent_service" { ... }

# After (v2)
resource "google_cloud_run_v2_service" "agent_service" { ... }
```

**Impact**: Tofu will want to destroy and recreate the service

**Mitigation**: Use Tofu state manipulation (see Rollback Strategy below)

### Template Structure Change
```hcl
# Before (v1)
template {
  spec {
    containers { ... }
  }
}

# After (v2)
template {
  containers { ... }  # No 'spec' wrapper
}
```

### IAM Resource Type Change
```hcl
# Before (v1)
resource "google_cloud_run_service_iam_member" "public_access" { ... }

# After (v2)
resource "google_cloud_run_v2_service_iam_member" "public_access" { ... }
```

---

## Step-by-Step Migration (Example: practices_service)

### Step 1: Backup Current Configuration

```bash
cd infra
tofu state pull > backup-pre-v2-migration.tfstate
cp modules/practices/main.tf modules/practices/main.tf.v1.backup
```

### Step 2: Update Module to v2

**Edit `infra/modules/practices/main.tf`**:

**Before (v1)**:
```hcl
resource "google_cloud_run_service" "practices" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    spec {
      container_concurrency = 20
      containers {
        image = var.image

        ports {
          container_port = 8000
        }

        env {
          name  = "API_VERSION"
          value = "0.1.0"
        }

        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }

        dynamic "env" {
          for_each = var.env
          content {
            name  = env.key
            value = env.value
          }
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }

      service_account_name = var.service_account_email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  autogenerate_revision_name = true

  metadata {
    annotations = {
      "autoscaling.knative.dev/minScale" = "1"
    }
  }
}

resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.practices.location
  project  = google_cloud_run_service.practices.project
  service  = google_cloud_run_service.practices.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

**After (v2)**:
```hcl
resource "google_cloud_run_v2_service" "practices" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    # Execution environment gen2 (faster cold starts)
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    # Scaling configuration
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    # Container configuration
    containers {
      image = var.image

      ports {
        container_port = 8000
      }

      env {
        name  = "API_VERSION"
        value = "0.1.0"
      }

      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }

      dynamic "env" {
        for_each = var.env
        content {
          name  = env.key
          value = env.value
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = false  # Always-allocated CPU
        startup_cpu_boost = true   # Faster cold starts
      }

      # Startup probe (recommended)
      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 0
        timeout_seconds       = 1
        period_seconds        = 3
        failure_threshold     = 10
      }

      # Liveness probe (optional)
      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 30
        timeout_seconds       = 1
        period_seconds        = 10
        failure_threshold     = 3
      }
    }

    service_account = var.service_account_email

    # VPC configuration (optional, can add later)
    # vpc_access {
    #   connector = var.vpc_connector_id
    #   egress    = "PRIVATE_RANGES_ONLY"
    # }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Ingress control (can restrict to internal later)
  ingress = "INGRESS_TRAFFIC_ALL"  # or "INGRESS_TRAFFIC_INTERNAL_ONLY"
}

# IAM binding for v2
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.practices.location
  project  = google_cloud_run_v2_service.practices.project
  name     = google_cloud_run_v2_service.practices.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

**Key Differences**:
1. Resource type: `google_cloud_run_service` → `google_cloud_run_v2_service`
2. No `spec` wrapper in template
3. `execution_environment = "EXECUTION_ENVIRONMENT_GEN2"`
4. Scaling: `metadata.annotations` → `scaling` block
5. Resources: `cpu_idle` and `startup_cpu_boost` options
6. Probes: Native `startup_probe` and `liveness_probe`
7. Service account: `service_account_name` → `service_account`
8. IAM: `google_cloud_run_service_iam_member` → `google_cloud_run_v2_service_iam_member`
9. IAM service reference: `service` → `name`

### Step 3: Plan the Change

```bash
cd infra
tofu plan -var-file=staging.auto.tfvars

# Expected output:
# - google_cloud_run_service.practices will be destroyed
# - google_cloud_run_v2_service.practices will be created
# - google_cloud_run_service_iam_member.public_access will be destroyed
# - google_cloud_run_v2_service_iam_member.public_access will be created
```

**⚠️ WARNING**: Tofu will destroy and recreate the service (brief downtime)

### Step 4: Apply in Staging

```bash
cd infra
tofu apply -var-file=staging.auto.tfvars

# Confirm: yes

# Watch for successful creation
# Check Cloud Console: Cloud Run → practices-service → should show v2 icon
```

### Step 5: Validate Migration

**Health Check**:
```bash
# Get service URL
STAGING_URL=$(gcloud run services describe practices-service \
  --region=us-east4 \
  --project=mindmirror-staging \
  --format='value(status.url)')

# Test health endpoint
curl $STAGING_URL/health

# Expected: {"status": "healthy"}
```

**GraphQL Gateway Integration**:
```bash
# Query gateway
curl -X POST https://gateway-staging.run.app/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ practices { id name } }"}'

# Expected: GraphQL response with practices data
```

**Logs Check**:
```bash
# Check logs for errors
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=practices-service" \
  --limit=50 \
  --project=mindmirror-staging

# Look for startup errors, connection failures, etc.
```

**Performance Check**:
```bash
# Cold start time (first request after scale-to-zero)
time curl $STAGING_URL/health

# Should be faster with gen2 (< 2 seconds)
```

### Step 6: Update Gateway Configuration (if needed)

**If gateway hardcodes service URLs**:
```bash
# Update gateway env var with new v2 URL (should be same URL)
# Gateway should auto-detect v2 services

# If issues, run gateway schema composition
./scripts/update-gateway.sh practices_service
```

### Step 7: Monitor for 24 Hours

**What to watch**:
- Error rate (should be near zero)
- Latency (should be same or better)
- Cold start performance (should be faster)
- Database connection errors (should be none)
- Memory usage (should be similar)

**If issues detected**:
- Review logs for error patterns
- Check resource limits (CPU/memory sufficient?)
- Verify probes not causing restarts
- Consider rollback if critical

### Step 8: Apply to Production

**After 24 hours of stable staging**:

```bash
cd infra
tofu plan -var-file=production.auto.tfvars
tofu apply -var-file=production.auto.tfvars

# Repeat validation steps for production
```

---

## Service-Specific Migration Notes

### agent_service (Complex)
**Considerations**:
- High memory usage (AI/embeddings) → may need 2Gi+ memory
- Calls external APIs (OpenAI, Qdrant) → verify egress works
- Storage access (GCS for prompts) → verify SA permissions
- Longer cold starts → tune startup probe timeouts

**Recommended Settings**:
```hcl
resources {
  limits = {
    cpu    = "2"
    memory = "2Gi"
  }
  cpu_idle          = false
  startup_cpu_boost = true
}

startup_probe {
  http_get {
    path = "/health"
  }
  initial_delay_seconds = 0
  timeout_seconds       = 3
  period_seconds        = 5
  failure_threshold     = 15  # More lenient for AI service
}
```

### celery_worker_web (Pub/Sub Integration)
**Considerations**:
- Pub/Sub push subscriptions → verify endpoint URLs update
- Background task execution → may need longer timeouts
- Connects to multiple services → verify service discovery

**Post-Migration**:
```bash
# Verify Pub/Sub subscriptions updated
gcloud pubsub subscriptions describe journal-indexing-sub \
  --project=mindmirror-staging

# Check push_config.push_endpoint matches new v2 URL
```

### gateway (Critical Path)
**Considerations**:
- Public-facing → high availability critical
- Federation layer → verify schema composition
- JWT validation → test authentication flow
- Migrate LAST (after all backends migrated)

**Testing**:
```bash
# Full integration test
# 1. Test unauthenticated queries (public queries)
# 2. Test authenticated queries (JWT token)
# 3. Test mutations (create, update, delete)
# 4. Test subscriptions (if applicable)
# 5. Load test (ensure can handle traffic)
```

---

## Advanced v2 Features (Phase 2)

### Feature 1: Secret Volumes

**Before (env vars)**:
```hcl
env {
  name  = "DATABASE_URL"
  value = var.database_url  # Visible in Cloud Console
}
```

**After (volume mounts)**:
```hcl
template {
  volumes {
    name = "secrets"
    secret {
      secret       = "DATABASE_URL"
      default_mode = 0444
      items {
        path    = "DATABASE_URL"
        version = "latest"
      }
    }
  }

  containers {
    volume_mounts {
      name       = "secrets"
      mount_path = "/secrets"
    }

    env {
      name  = "DATABASE_URL_FILE"
      value = "/secrets/DATABASE_URL"
    }
  }
}
```

**Application Code Change** (Python):
```python
# shared/secrets.py
import os

def get_secret(secret_name: str) -> str:
    """Read secret from file or fallback to env var."""
    file_path = os.getenv(f"{secret_name}_FILE")
    if file_path and os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return os.getenv(secret_name)

# Usage in services
DATABASE_URL = get_secret("DATABASE_URL")
```

### Feature 2: VPC Networking

**Add VPC connector**:
```hcl
template {
  vpc_access {
    connector = google_vpc_access_connector.connector.id
    egress    = "PRIVATE_RANGES_ONLY"  # VPC traffic through VPC, public through internet
  }

  containers {
    # ... rest of config
  }
}
```

**Benefit**: Backend services can communicate via internal IPs

### Feature 3: Internal Ingress

**Restrict backend services to internal-only**:
```hcl
resource "google_cloud_run_v2_service" "agent_service" {
  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"  # No public endpoint
  # ... rest of config
}

# Gateway remains public
resource "google_cloud_run_v2_service" "gateway" {
  ingress = "INGRESS_TRAFFIC_ALL"  # Public entry point
  # ... rest of config
}
```

**Result**: Backend services accessible only from gateway (or within VPC)

### Feature 4: Multiple Containers (Sidecars)

**Example: Cloud SQL Proxy sidecar**:
```hcl
template {
  containers {
    name  = "app"
    image = var.image
    # ... main app config
  }

  containers {
    name  = "cloud-sql-proxy"
    image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:latest"
    args  = ["--port=5432", "PROJECT:REGION:INSTANCE"]
  }
}
```

**Note**: MindMirror uses Supabase (external), so this is not immediately needed

---

## Rollback Strategy

### If Migration Fails (Staging)

**Option 1: Tofu State Manipulation (Preferred)**
```bash
# Remove v2 resources from state
tofu state rm google_cloud_run_v2_service.practices
tofu state rm google_cloud_run_v2_service_iam_member.public_access

# Restore v1 configuration
cp modules/practices/main.tf.v1.backup modules/practices/main.tf

# Import v1 service back into state
tofu import google_cloud_run_service.practices \
  projects/mindmirror-staging/locations/us-east4/services/practices-service

tofu import google_cloud_run_service_iam_member.public_access \
  "projects/mindmirror-staging/locations/us-east4/services/practices-service roles/run.invoker allUsers"

# Restore state
tofu plan -var-file=staging.auto.tfvars  # Should show no changes
```

**Option 2: Manual Revert via gcloud (Faster)**
```bash
# Deploy previous image tag manually
gcloud run deploy practices-service \
  --image=us-east4-docker.pkg.dev/mindmirror-staging/mindmirror/practices_service:PREVIOUS_TAG \
  --region=us-east4 \
  --project=mindmirror-staging

# Fix Tofu state to match reality
tofu refresh -var-file=staging.auto.tfvars
```

### If Migration Fails (Production)

**Same as staging, but MUCH more careful**:
1. Immediately notify team
2. Assess impact (is service down? partial outage?)
3. Execute rollback (state manipulation or gcloud)
4. Verify service restored
5. Post-mortem: why did it fail in production but not staging?

---

## Testing Checklist (Per Service)

Before considering a service migration complete:

- [ ] **Health Check**: `/health` endpoint returns 200 OK
- [ ] **GraphQL Integration**: Gateway can query the service
- [ ] **Database Access**: Service can read/write to database
- [ ] **External APIs**: Service can call external APIs (Supabase, OpenAI, etc.)
- [ ] **Secret Access**: Service can access secrets from Secret Manager
- [ ] **Logging**: Logs appear in Cloud Logging with correct labels
- [ ] **Metrics**: Metrics appear in Cloud Monitoring
- [ ] **Autoscaling**: Service scales up/down based on traffic
- [ ] **Cold Starts**: Startup probe allows sufficient time for initialization
- [ ] **Liveness**: Liveness probe doesn't cause false restarts
- [ ] **Performance**: Latency within acceptable range (p95 < 2s)
- [ ] **Error Rate**: Near-zero errors under normal load
- [ ] **Load Test**: Can handle expected production traffic
- [ ] **IAM**: Correct service account assigned, permissions work
- [ ] **24 Hour Stability**: No issues for 24 hours in staging

---

## Common Issues and Solutions

### Issue: Service Won't Start After Migration

**Symptoms**: Service shows "Revision failed" in Cloud Console

**Possible Causes**:
1. Startup probe timeout too short
2. Health endpoint not responding
3. Container port mismatch
4. Resource limits too low (OOM)

**Debugging**:
```bash
# Check revision logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=SERVICENAME AND severity>=ERROR" \
  --limit=50

# Check revision status
gcloud run revisions describe REVISION_NAME \
  --region=us-east4 \
  --format=json | jq '.status.conditions'
```

**Solutions**:
- Increase startup probe `failure_threshold` and `timeout_seconds`
- Verify health endpoint path and port
- Increase memory limit if OOM errors
- Remove probes temporarily to isolate issue

---

### Issue: Service Starts But Can't Access Database

**Symptoms**: Logs show connection errors, timeout, or authentication failures

**Possible Causes**:
1. Service account changed
2. Database credentials not accessible
3. VPC networking blocking traffic (if VPC enabled)

**Debugging**:
```bash
# Check service account
gcloud run services describe SERVICENAME \
  --region=us-east4 \
  --format="value(spec.template.spec.serviceAccountName)"

# Check IAM permissions
gcloud iam service-accounts get-iam-policy SERVICE_ACCOUNT_EMAIL

# Test database connection from Cloud Shell
gcloud run services proxy SERVICENAME --region=us-east4
# Then: psql $DATABASE_URL
```

**Solutions**:
- Verify `service_account` field in v2 config matches v1
- Verify Secret Manager IAM still grants access
- Check Supabase firewall allows Cloud Run IPs

---

### Issue: Gateway Can't Reach Backend Service

**Symptoms**: Gateway returns errors when querying backend

**Possible Causes**:
1. Service URL changed (unlikely, should be same)
2. IAM permissions changed
3. Backend service using internal ingress (gateway can't reach)

**Debugging**:
```bash
# Check gateway can reach backend
gcloud run services proxy gateway --region=us-east4
# From proxy shell:
curl https://agent-service-PROJECT.run.app/health

# Check IAM bindings
gcloud run services get-iam-policy agent-service \
  --region=us-east4
```

**Solutions**:
- Verify gateway SA has `run.invoker` on backend service
- If using internal ingress, ensure gateway in same VPC
- Update gateway env var if service URL changed

---

### Issue: Performance Degradation After Migration

**Symptoms**: Latency increased, cold starts slower

**Possible Causes**:
1. gen2 environment has different characteristics
2. Startup probe delaying traffic routing
3. Resource limits different (CPU/memory)

**Debugging**:
```bash
# Compare cold start times
# v1 service:
time curl https://v1-service.run.app/health

# v2 service:
time curl https://v2-service.run.app/health

# Check resource usage
gcloud monitoring time-series list \
  --filter='resource.labels.service_name="SERVICENAME"' \
  --format=json
```

**Solutions**:
- Enable `startup_cpu_boost = true`
- Set `cpu_idle = false` (always-allocated CPU)
- Tune startup probe initial delay
- Increase CPU/memory limits if needed

---

## Summary

**Migration Path**:
1. ✅ Start with simple service (practices)
2. ✅ Validate thoroughly in staging
3. ✅ Migrate one service per day
4. ✅ Save complex services (agent, gateway) for last
5. ✅ Add advanced features (VPC, secret volumes) after basic migration

**Success Criteria**:
- All 8 services on Cloud Run v2
- Same or better performance than v1
- No production incidents from migration
- Team comfortable with v2 configuration

**Timeline**: 1-2 weeks (9 services × 1 day each)

**Next Steps**: After v2 migration complete → enable VPC networking, secret volumes, internal ingress

---

## References

- [Cloud Run v2 Migration Guide](https://cloud.google.com/run/docs/migrating)
- [Cloud Run v2 API Reference](https://cloud.google.com/run/docs/reference/rest/v2/projects.locations.services)
- [Execution Environments](https://cloud.google.com/run/docs/about-execution-environments)
- [Startup and Liveness Probes](https://cloud.google.com/run/docs/configuring/healthchecks)
