# Infrastructure Production Readiness Audit

**Goal**: Identify gaps between current `infra/` setup and production-ready infrastructure
**Timeline**: End of 2025 (2 months)
**Approach**: Phased hardening with prioritized improvements

---

## Executive Summary

**Current State**: Working infrastructure with Cloud Run v1, public access to all services, secrets via environment variables

**Production Gaps Identified**:
- 🔴 **CRITICAL** (Security): All services publicly accessible (`allUsers` IAM)
- 🔴 **CRITICAL** (Security): Secrets exposed via environment variables (not volume mounts)
- 🔴 **CRITICAL** (Architecture): Using legacy Cloud Run v1 (missing v2 features)
- 🟡 **IMPORTANT** (Networking): No VPC networking, services on public internet
- 🟡 **IMPORTANT** (IAM): Broad IAM permissions (project-level vs resource-level)
- 🟡 **IMPORTANT** (Observability): No Cloud Monitoring, logging, alerting
- 🟢 **RECOMMENDED** (Resource Management): No autoscaling limits, CPU/memory fixed
- 🟢 **RECOMMENDED** (Cost Optimization): Always-on min instances (cost in staging)

---

## Detailed Gap Analysis

### 1. Security Issues (CRITICAL)

#### 1.1 Public Access to All Services
**Current State**:
```hcl
# Every service module has this:
resource "google_cloud_run_service_iam_member" "public_access" {
  role   = "roles/run.invoker"
  member = "allUsers"  # ⚠️ CRITICAL SECURITY GAP
}
```

**Impact**:
- ALL backend services are publicly accessible without authentication
- Agent Service, Journal Service, Habits, Meals, Movements, Practices, Users - all exposed
- Only Gateway should be public (frontend entry point)
- Backend services should require authentication from Gateway

**Fix Required**:
```hcl
# Backend services: REMOVE public access
# resource "google_cloud_run_service_iam_member" "public_access" { ... } ← DELETE

# Backend services: ADD gateway-only access
resource "google_cloud_run_service_iam_member" "gateway_access" {
  service = google_cloud_run_service.agent_service.name
  role    = "roles/run.invoker"
  member  = "serviceAccount:${var.gateway_service_account_email}"
}

# Gateway: KEEP public access (it's the entry point)
resource "google_cloud_run_service_iam_member" "public_access" {
  service = google_cloud_run_service.gateway.name
  role    = "roles/run.invoker"
  member  = "allUsers"  # ✅ OK for gateway only
}
```

**Effort**: 2-3 hours
**Priority**: 🔴 CRITICAL - Must fix before production launch

---

#### 1.2 Secrets via Environment Variables
**Current State**:
```hcl
# All services expose secrets as env vars
env {
  name  = "DATABASE_URL"
  value = var.database_url  # ⚠️ Visible in console, logs, env dumps
}

env {
  name  = "SUPABASE_SERVICE_ROLE_KEY"
  value = var.supabase_service_role_key  # ⚠️ High-value credential exposed
}

env {
  name  = "OPENAI_API_KEY"
  value = var.openai_api_key  # ⚠️ API key in plaintext env
}
```

**Impact**:
- Secrets visible in Cloud Console UI (environment variables tab)
- Secrets appear in logs if application dumps environment
- Secrets accessible to anyone with `roles/run.viewer` permission
- Compliance issues (SOC2, HIPAA, PCI if applicable)

**Fix Required (Cloud Run v2)**:
```hcl
# Cloud Run v2 supports secret volumes
resource "google_cloud_run_v2_service" "agent_service" {
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

      # Application reads from file instead of env var
      env {
        name  = "DATABASE_URL_FILE"
        value = "/secrets/DATABASE_URL"
      }
    }
  }
}
```

**Code Changes Required**: Applications must support reading secrets from files
**Effort**: 1-2 days (infra changes + app code changes + testing)
**Priority**: 🔴 CRITICAL - Production security requirement

---

#### 1.3 IAM Permissions Too Broad
**Current State**:
```hcl
# Project-level permissions granted to service accounts
resource "google_project_iam_member" "agent_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"  # ⚠️ ALL secrets in project
  member  = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_project_iam_member" "celery_worker_sa_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"  # ⚠️ Can invoke ANY Cloud Run service
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}
```

**Impact**:
- Service accounts have access to ALL secrets, not just their own
- Celery worker can invoke ANY Cloud Run service, not just agent/journal
- Violates principle of least privilege
- Lateral movement risk if one service is compromised

**Fix Required**:
```hcl
# Resource-level IAM instead of project-level
resource "google_secret_manager_secret_iam_member" "agent_sa_database_url" {
  secret_id = google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_cloud_run_service_iam_member" "celery_agent_invoker" {
  service = google_cloud_run_service.agent_service.name  # Specific service only
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}
```

**Effort**: 3-4 hours
**Priority**: 🟡 IMPORTANT - Should fix before production

---

### 2. Architecture Issues (CRITICAL)

#### 2.1 Cloud Run v1 (Legacy) vs v2
**Current State**: All services use `google_cloud_run_service` (v1 API)

**Missing v2 Features**:
- **VPC Networking**: v1 cannot connect to VPC, v2 supports VPC Direct (private IPs)
- **Secret Volumes**: v1 only supports env vars, v2 supports mounted secret files
- **Execution Environment**: v1 uses gen1, v2 uses gen2 (faster cold starts, more memory)
- **Startup/Liveness Probes**: v2 has native support, v1 requires workarounds
- **Multi-Container Support**: v2 supports sidecars (e.g., Cloud SQL Proxy), v1 single container only
- **Direct VPC Egress**: v2 can route directly to VPC without Serverless VPC Connector
- **Service Mesh Integration**: v2 integrates with Istio/Anthos Service Mesh

**Migration Required**:
```hcl
# Before (v1)
resource "google_cloud_run_service" "agent_service" {
  name     = "agent-service"
  location = var.region
  template {
    spec {
      containers { ... }
    }
  }
}

# After (v2)
resource "google_cloud_run_v2_service" "agent_service" {
  name     = "agent-service"
  location = var.region

  template {
    # VPC networking support
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"  # Route VPC traffic through VPC
    }

    # Secret volumes support
    volumes {
      name = "secrets"
      secret { ... }
    }

    containers {
      image = var.agent_service_container_image

      # Startup probe for health checks
      startup_probe {
        http_get {
          path = "/health"
        }
      }

      # Liveness probe
      liveness_probe {
        http_get {
          path = "/health"
        }
      }

      volume_mounts {
        name       = "secrets"
        mount_path = "/secrets"
      }
    }

    # Execution environment gen2
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
  }
}
```

**Breaking Changes**:
- Resource name: `google_cloud_run_service` → `google_cloud_run_v2_service`
- Template structure: `spec` → direct `containers`
- IAM bindings: `google_cloud_run_service_iam_member` → `google_cloud_run_v2_service_iam_member`

**Migration Strategy**:
1. Migrate one service at a time (start with non-critical service like practices)
2. Test in staging thoroughly before production
3. Use Terraform state manipulation to avoid recreating services:
   ```bash
   tofu state mv google_cloud_run_service.practices google_cloud_run_v2_service.practices
   ```
4. Update application code to support secret files (if using secret volumes)

**Effort**: 1-2 days per service (8 services total = 2-3 weeks)
**Priority**: 🔴 CRITICAL - Required for VPC networking and secret volumes

---

### 3. Networking Issues (IMPORTANT)

#### 3.1 No VPC Networking
**Current State**: All services communicate over public internet

**Impact**:
- Backend service-to-service traffic goes over public internet (even within same project)
- Cannot use private IPs for databases (Supabase is external, but if self-hosted PostgreSQL)
- Cannot restrict backend services to VPC-only traffic
- Increased attack surface (public endpoints)

**Fix Required**:
```hcl
# Create VPC network
resource "google_compute_network" "mindmirror" {
  name                    = "mindmirror-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}

# Create subnet for Cloud Run
resource "google_compute_subnetwork" "cloudrun" {
  name          = "cloudrun-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.mindmirror.id

  # Private Google Access for GCS, Secret Manager, etc.
  private_ip_google_access = true
}

# Create VPC Access Connector for Cloud Run v2
resource "google_vpc_access_connector" "connector" {
  name          = "cloudrun-connector"
  region        = var.region
  network       = google_compute_network.mindmirror.name
  ip_cidr_range = "10.8.0.0/28"  # /28 = 16 IPs (minimum)
}

# Update Cloud Run v2 services to use VPC
resource "google_cloud_run_v2_service" "agent_service" {
  template {
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"  # Only VPC traffic through VPC
    }
  }
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal-cloudrun"
  network = google_compute_network.mindmirror.name

  allow {
    protocol = "tcp"
    ports    = ["8000", "8001", "8003", "8004", "8005", "8006", "8007", "4000"]
  }

  source_ranges = ["10.0.0.0/24"]  # Only from Cloud Run subnet
}
```

**Prerequisites**: Cloud Run v2 migration (v1 doesn't support VPC)

**Effort**: 4-6 hours (VPC setup + connector + testing)
**Priority**: 🟡 IMPORTANT - Network isolation and security

---

#### 3.2 Internal Service Communication
**Current State**: Services communicate via public URLs

**Example (Journal Service calling Agent Service)**:
```hcl
env {
  name  = "AGENT_SERVICE_URL"
  value = var.agent_service_url  # https://agent-service-xxx.run.app (public)
}
```

**Fix Required (with VPC)**:
```hcl
# Option 1: Keep public URLs but restrict IAM
# (Already covered in 1.1 - gateway-only access)

# Option 2: Use internal ingress (Cloud Run v2)
resource "google_cloud_run_v2_service" "agent_service" {
  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"  # No public access at all

  template {
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "ALL_TRAFFIC"  # Route everything through VPC
    }
  }
}

# Gateway remains public
resource "google_cloud_run_v2_service" "gateway" {
  ingress = "INGRESS_TRAFFIC_ALL"  # Public access
}
```

**Benefit**: Backend services have NO public endpoint (100% internal)

**Effort**: 2-3 hours
**Priority**: 🟡 IMPORTANT - Defense in depth

---

### 4. Observability Gaps (IMPORTANT)

#### 4.1 No Cloud Monitoring or Alerting
**Current State**: No monitoring dashboards, no alerts

**Impact**:
- No visibility into service health, latency, errors
- Cannot detect outages or performance degradation
- No alerting for critical failures
- Difficult to debug production issues

**Fix Required**:
```hcl
# Uptime checks for critical services
resource "google_monitoring_uptime_check_config" "gateway" {
  display_name = "Gateway Health Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/healthcheck"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "${google_cloud_run_service.gateway.status[0].url}"
    }
  }
}

# Alert policies
resource "google_monitoring_alert_policy" "gateway_down" {
  display_name = "Gateway Down"
  combiner     = "OR"

  conditions {
    display_name = "Gateway Uptime Check Failed"

    condition_threshold {
      filter          = "resource.type=\"uptime_url\" AND metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\""
      duration        = "60s"
      comparison      = "COMPARISON_LT"
      threshold_value = 1
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}

# Notification channels
resource "google_monitoring_notification_channel" "email" {
  display_name = "Ops Team Email"
  type         = "email"

  labels = {
    email_address = "ops@mindmirror.app"
  }
}

# Log-based metrics
resource "google_logging_metric" "error_rate" {
  name   = "error_rate"
  filter = "severity>=ERROR AND resource.type=\"cloud_run_revision\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# Alert on high error rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 10/min"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/error_rate\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}
```

**Effort**: 1 day (setup dashboards, alerts, runbooks)
**Priority**: 🟡 IMPORTANT - Production visibility

---

#### 4.2 No Structured Logging
**Current State**: Applications log to stdout (basic Cloud Logging)

**Improvement**:
```hcl
# Application code should use structured logging (JSON)
# Example Python:
import logging
import json_logging

json_logging.init_fastapi(enable_json=True)
logger = logging.getLogger(__name__)

logger.info("User login", extra={
    "user_id": user_id,
    "ip_address": request.client.host,
    "request_id": request.state.request_id
})
```

**Benefit**: Easier log querying, better correlation, exportable to BigQuery

**Effort**: 2-3 days (update all services)
**Priority**: 🟢 RECOMMENDED - Nice to have, not critical

---

### 5. Resource Management Issues (RECOMMENDED)

#### 5.1 No Autoscaling Limits
**Current State**:
```hcl
metadata {
  annotations = {
    "autoscaling.knative.dev/minScale" = "1"  # Always 1 instance minimum
    # No maxScale set = unlimited
  }
}
```

**Impact**:
- Services can scale to 100s of instances under load (good for availability)
- But no cost protection (could get expensive under DDoS or traffic spike)
- No graceful degradation strategy

**Fix Required**:
```hcl
metadata {
  annotations = {
    "autoscaling.knative.dev/minScale"         = "1"  # Staging: 1, Production: 2
    "autoscaling.knative.dev/maxScale"         = "10"  # Cap maximum instances
    "run.googleapis.com/cpu-throttling"        = "false"  # Always-allocated CPU
    "run.googleapis.com/startup-cpu-boost"     = "true"   # Faster cold starts
  }
}
```

**Cost Optimization (Staging)**:
```hcl
# Staging can scale to zero to save cost
metadata {
  annotations = {
    "autoscaling.knative.dev/minScale" = var.environment == "production" ? "1" : "0"
    "autoscaling.knative.dev/maxScale" = var.environment == "production" ? "10" : "3"
  }
}
```

**Effort**: 1-2 hours
**Priority**: 🟢 RECOMMENDED - Cost control and scaling strategy

---

#### 5.2 Fixed CPU/Memory Resources
**Current State**:
```hcl
resources {
  limits = {
    cpu    = "1"      # Fixed 1 CPU
    memory = "512Mi"  # Fixed 512MB
  }
}
```

**Impact**:
- Under-provisioned services may be slow or crash (OOM)
- Over-provisioned services waste money
- No differentiation by service needs (agent service needs more memory than habits)

**Fix Required**:
```hcl
# Right-size per service based on actual usage
# Agent service (AI/embeddings = memory-intensive)
resources {
  limits = {
    cpu    = "2"
    memory = "2Gi"
  }
}

# Gateway (lightweight proxy)
resources {
  limits = {
    cpu    = "1"
    memory = "512Mi"
  }
}

# Use variables for flexibility
resources {
  limits = {
    cpu    = var.cpu_limit
    memory = var.memory_limit
  }
}
```

**Process**:
1. Monitor actual resource usage in staging for 1-2 weeks
2. Right-size based on p95 CPU/memory usage
3. Add 20-30% headroom for spikes

**Effort**: Ongoing (monitor → adjust → repeat)
**Priority**: 🟢 RECOMMENDED - Performance and cost optimization

---

### 6. State Management Issues (INFORMATIONAL)

#### 6.1 Hardcoded State Backend
**Current State**:
```hcl
terraform {
  backend "gcs" {
    bucket  = "mindmirror-tofu-state"  # ⚠️ Hardcoded
    prefix  = "envs/default"
  }
}
```

**Impact**:
- Staging and production share same state bucket name (different prefixes)
- Cannot easily switch backends per environment
- State bucket must exist before terraform init

**Fix Required (Partial Backend Config)**:
```hcl
# versions.tf - remove hardcoded backend
terraform {
  backend "gcs" {}  # Empty = configured via CLI or -backend-config
}

# Use backend config files per environment
# backend-staging.hcl
bucket = "mindmirror-staging-tofu-state"
prefix = "envs/staging"

# backend-production.hcl
bucket = "mindmirror-production-tofu-state"
prefix = "envs/production"

# Initialize per environment
tofu init -backend-config=backend-staging.hcl
```

**Benefit**: Clearer separation, easier to manage different backends

**Effort**: 1 hour
**Priority**: 🟢 RECOMMENDED - Better organization, not critical

---

## Prioritized Roadmap

### Phase 1: Pre-Production Critical (Week 1-2)
**Goal**: Make infrastructure secure enough for production launch

| Task | Effort | Status |
|------|--------|--------|
| 1.1 Remove public access from backend services | 2-3 hours | 🔴 CRITICAL |
| 1.3 Narrow IAM permissions to resource-level | 3-4 hours | 🟡 IMPORTANT |
| 2.1 Migrate one service to Cloud Run v2 (pilot) | 1 day | 🔴 CRITICAL |
| Test v2 migration in staging | 2 hours | 🔴 CRITICAL |

**Deliverable**: Backend services no longer publicly accessible, Cloud Run v2 pilot successful

---

### Phase 2: Production Hardening (Week 3-4)
**Goal**: Complete v2 migration and add networking layer

| Task | Effort | Status |
|------|--------|--------|
| 2.1 Migrate remaining 7 services to Cloud Run v2 | 1-2 weeks | 🔴 CRITICAL |
| 1.2 Implement secret volumes (requires v2) | 1-2 days | 🔴 CRITICAL |
| 3.1 Setup VPC networking | 4-6 hours | 🟡 IMPORTANT |
| 3.2 Configure internal ingress for backend services | 2-3 hours | 🟡 IMPORTANT |
| 4.1 Setup basic monitoring and alerting | 1 day | 🟡 IMPORTANT |

**Deliverable**: All services on Cloud Run v2, VPC networking active, secrets via volume mounts, basic monitoring

---

### Phase 3: Polish and Optimization (Week 5-6)
**Goal**: Cost optimization and operational maturity

| Task | Effort | Status |
|------|--------|--------|
| 5.1 Configure autoscaling limits | 1-2 hours | 🟢 RECOMMENDED |
| 5.2 Right-size CPU/memory per service | Ongoing | 🟢 RECOMMENDED |
| 4.2 Implement structured logging | 2-3 days | 🟢 RECOMMENDED |
| 6.1 Separate state backends per environment | 1 hour | 🟢 RECOMMENDED |
| Documentation and runbooks | 2-3 days | 🟢 RECOMMENDED |

**Deliverable**: Optimized resource usage, better observability, operational documentation

---

## Success Criteria

**By Week 2** (Pre-Production):
- ✅ All backend services require authentication (no public access)
- ✅ At least 1 service migrated to Cloud Run v2 successfully
- ✅ IAM permissions narrowed to resource-level

**By Week 4** (Production Launch):
- ✅ All services on Cloud Run v2
- ✅ Secrets loaded via volume mounts (not env vars)
- ✅ VPC networking active
- ✅ Backend services use internal ingress only
- ✅ Basic uptime monitoring and alerting configured

**By Week 6** (Operational Maturity):
- ✅ Autoscaling limits configured
- ✅ Resources right-sized per service
- ✅ Structured logging implemented
- ✅ Runbooks and documentation complete

---

## Cost Impact Analysis

### Current Monthly Cost (Estimated)
- 8 services × 1 min instance × $0.00002400/vCPU-second × 730 hours = ~$100-150/month
- Artifact Registry: ~$5-10/month
- **Total**: ~$105-160/month

### Post-Hardening Cost (Estimated)
- VPC Connector: ~$10/month (fixed cost)
- Same Cloud Run costs (no change)
- Monitoring (free tier): $0
- **Total**: ~$115-170/month

**Cost increase**: ~$10-15/month for VPC networking (acceptable for security benefit)

---

## Workload Identity Federation (WIF) Integration

**Context**: User requested WIF instead of service account keys for GitHub Actions

**When to implement**: After Cloud Run v2 migration complete

**Why**: WIF provides keyless authentication from GitHub → GCP, eliminating long-lived SA keys

**Implementation**: See companion document `docs/wif-setup.md` (to be created)

---

## Next Steps

1. **Review this audit** with team/stakeholders
2. **Prioritize tasks** based on timeline (2 months to production)
3. **Start Phase 1** (remove public access + Cloud Run v2 pilot)
4. **Create companion docs**:
   - `docs/cloud-run-v2-migration.md` - Step-by-step v1 → v2 guide
   - `docs/vpc-networking-strategy.md` - VPC design and implementation
   - `docs/wif-setup.md` - Workload Identity Federation setup
   - `docs/iam-security-improvements.md` - Resource-level IAM patterns
   - `docs/production-hardening-checklist.md` - Acceptance criteria per phase

---

## Questions for User

1. **Environment strategy**: Should staging also scale to 0 (cost savings) or always have 1 instance (faster dev workflow)?

2. **Secret migration**: Can application code be updated to support reading secrets from files? Or should we keep env vars for now (less secure)?

3. **VPC priority**: Is VPC networking a hard requirement for production launch, or can it be Phase 3?

4. **Monitoring budget**: Are we OK with Cloud Monitoring costs (~$0.50-2/month per service for custom metrics)?

5. **Rollout strategy**: Gradual rollout (1 service at a time to production) or big-bang (all services updated in one deploy)?
