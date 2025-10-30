# IAM Security Improvements

**Goal**: Implement least-privilege IAM permissions following security best practices
**Current State**: Broad project-level permissions, public access to all services
**Target State**: Resource-specific permissions, gateway-only access for backends

---

## Security Principles

1. **Least Privilege**: Grant minimum permissions needed for functionality
2. **Resource-Level IAM**: Use specific resource bindings, not project-level
3. **Defense in Depth**: Multiple layers (IAM + VPC + ingress control)
4. **Separation of Duties**: Different SAs for different purposes
5. **Zero Trust**: Don't trust internal network position alone

---

## Current IAM Issues

### Issue 1: Public Access to All Services ❌

**Current**:
```hcl
# Every service has this
resource "google_cloud_run_service_iam_member" "public_access" {
  service = google_cloud_run_service.agent_service.name
  role    = "roles/run.invoker"
  member  = "allUsers"  # ⚠️ Anyone on internet can invoke
}
```

**Impact**: ALL backend services publicly accessible without authentication

### Issue 2: Project-Level Secret Access ❌

**Current**:
```hcl
# Service account can access ALL secrets in project
resource "google_project_iam_member" "agent_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.agent_service.email}"
}
```

**Impact**: Agent service can read ALL secrets (database, API keys, other services' credentials)

### Issue 3: Project-Level Cloud Run Invoker ❌

**Current**:
```hcl
# Celery worker can invoke ANY Cloud Run service
resource "google_project_iam_member" "celery_worker_sa_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}
```

**Impact**: Celery worker can invoke any service, not just agent/journal

---

## Improved IAM Architecture

### Layer 1: Remove Public Access from Backends

**Gateway ONLY should be public**:

```hcl
# Gateway: PUBLIC (entry point from internet)
resource "google_cloud_run_v2_service_iam_member" "gateway_public" {
  location = google_cloud_run_v2_service.gateway.location
  project  = google_cloud_run_v2_service.gateway.project
  name     = google_cloud_run_v2_service.gateway.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Backend services: NO public access
# Delete all "allUsers" IAM bindings from:
# - agent_service
# - journal_service
# - habits_service
# - meals_service
# - movements_service
# - practices_service
# - users_service
# - celery_worker_web
```

### Layer 2: Gateway-Only Access for Backends

**Grant gateway SA permission to invoke backends**:

```hcl
# Agent service: only gateway can invoke
resource "google_cloud_run_v2_service_iam_member" "agent_gateway_access" {
  location = google_cloud_run_v2_service.agent_service.location
  project  = google_cloud_run_v2_service.agent_service.project
  name     = google_cloud_run_v2_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.gateway.email}"
}

# Repeat for all backend services
# - journal_service
# - habits_service
# - meals_service
# - movements_service
# - practices_service
# - users_service
```

### Layer 3: Resource-Level Secret Access

**Grant each service access ONLY to secrets it needs**:

```hcl
# Agent service needs: DATABASE_URL, OPENAI_API_KEY, QDRANT_API_KEY, etc.
resource "google_secret_manager_secret_iam_member" "agent_database" {
  secret_id = google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_secret_manager_secret_iam_member" "agent_openai" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_service.email}"
}

# Journal service needs: DATABASE_URL, REDIS_URL, SUPABASE keys
resource "google_secret_manager_secret_iam_member" "journal_database" {
  secret_id = google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.journal_service.email}"
}

# ... etc for each service
```

### Layer 4: Service-Specific Run Invoker

**Celery worker can ONLY invoke services it needs**:

```hcl
# Celery worker → agent service (for indexing tasks)
resource "google_cloud_run_v2_service_iam_member" "celery_agent_invoker" {
  location = google_cloud_run_v2_service.agent_service.location
  project  = google_cloud_run_v2_service.agent_service.project
  name     = google_cloud_run_v2_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.celery_worker.email}"
}

# Celery worker → journal service (for journal indexing)
resource "google_cloud_run_v2_service_iam_member" "celery_journal_invoker" {
  location = google_cloud_run_v2_service.journal_service.location
  project  = google_cloud_run_v2_service.journal_service.project
  name     = google_cloud_run_v2_service.journal_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.celery_worker.email}"
}

# Remove project-level "roles/run.invoker" binding
```

---

## Service Account Permissions Matrix

| Service | Secrets Needed | Services Can Invoke | Storage Access |
|---------|---------------|-------------------|----------------|
| **agent_service** | DATABASE_URL, OPENAI_API_KEY, QDRANT_API_KEY, REDIS_URL, SUPABASE_* | None | GCS (traditions bucket - object admin) |
| **journal_service** | DATABASE_URL, REDIS_URL, SUPABASE_*, REINDEX_SECRET_KEY | agent_service (via HTTP) | None |
| **habits_service** | DATABASE_URL | None | None |
| **meals_service** | DATABASE_URL | None | None |
| **movements_service** | DATABASE_URL | None | None |
| **practices_service** | DATABASE_URL | None | None |
| **users_service** | DATABASE_URL | None | None |
| **celery_worker** | DATABASE_URL, REDIS_URL, QDRANT_API_KEY, OPENAI_API_KEY | agent_service, journal_service | None |
| **gateway** | SUPABASE_ANON_KEY, SUPABASE_JWT_SECRET | All backend services | None |

---

## Implementation Guide

### Step 1: Document Current Permissions

```bash
# List all IAM bindings for each service account
for SA in agent-service journal-service habits-service meals-service movements-service practices-service users-service celery-worker gateway; do
  echo "=== $SA ==="
  gcloud iam service-accounts get-iam-policy ${SA}@mindmirror-staging.iam.gserviceaccount.com \
    --project=mindmirror-staging

  # Also check what this SA can access
  gcloud projects get-iam-policy mindmirror-staging \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SA}@mindmirror-staging.iam.gserviceaccount.com" \
    --format="table(bindings.role)"
done > current-iam-state.txt
```

### Step 2: Create Secret Access Matrix

**Edit `infra/base/secrets.tf`** (new file):

```hcl
# Define all secrets (data sources)
data "google_secret_manager_secret" "database_url" {
  secret_id = "DATABASE_URL"
  project   = var.project_id
}

data "google_secret_manager_secret" "openai_api_key" {
  secret_id = "OPENAI_API_KEY"
  project   = var.project_id
}

data "google_secret_manager_secret" "qdrant_api_key" {
  secret_id = "QDRANT_API_KEY"
  project   = var.project_id
}

data "google_secret_manager_secret" "redis_url" {
  secret_id = "REDIS_URL"
  project   = var.project_id
}

# ... all other secrets

# Grant agent service access to its secrets
resource "google_secret_manager_secret_iam_member" "agent_database" {
  secret_id = data.google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_secret_manager_secret_iam_member" "agent_openai" {
  secret_id = data.google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_secret_manager_secret_iam_member" "agent_qdrant" {
  secret_id = data.google_secret_manager_secret.qdrant_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_secret_manager_secret_iam_member" "agent_redis" {
  secret_id = data.google_secret_manager_secret.redis_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agent_service.email}"
}

# Grant journal service access to its secrets
resource "google_secret_manager_secret_iam_member" "journal_database" {
  secret_id = data.google_secret_manager_secret.database_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.journal_service.email}"
}

resource "google_secret_manager_secret_iam_member" "journal_redis" {
  secret_id = data.google_secret_manager_secret.redis_url.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.journal_service.email}"
}

# ... repeat for all services and their secrets
```

### Step 3: Remove Project-Level IAM Bindings

**Edit `infra/base/main.tf`**:

**Remove these blocks**:
```hcl
# DELETE: Project-level secret access
resource "google_project_iam_member" "agent_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.agent_service.email}"
}

# DELETE: Project-level run invoker
resource "google_project_iam_member" "celery_worker_sa_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.celery_worker.email}"
}

# DELETE ALL project-level IAM bindings
# Replace with resource-specific bindings
```

### Step 4: Add Gateway-Only Access to Backends

**Edit each service module** (e.g., `infra/modules/agent_service/main.tf`):

**Remove**:
```hcl
# DELETE: Public access
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name   = google_cloud_run_v2_service.agent_service.name
  role   = "roles/run.invoker"
  member = "allUsers"
}
```

**Add**:
```hcl
# ADD: Gateway-only access
resource "google_cloud_run_v2_service_iam_member" "gateway_access" {
  location = google_cloud_run_v2_service.agent_service.location
  project  = google_cloud_run_v2_service.agent_service.project
  name     = google_cloud_run_v2_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.gateway_service_account_email}"
}
```

**Update module variables**:
```hcl
# infra/modules/agent_service/variables.tf
variable "gateway_service_account_email" {
  description = "Email of gateway service account (for invoker IAM)"
  type        = string
}
```

**Pass from main.tf**:
```hcl
# infra/main.tf
module "agent_service" {
  source = "./modules/agent_service"

  # ... existing variables

  gateway_service_account_email = google_service_account.gateway.email
}
```

### Step 5: Test Incrementally

**Test after each change**:

```bash
# 1. Apply IAM changes
cd infra
tofu plan -var-file=staging.auto.tfvars
tofu apply -var-file=staging.auto.tfvars

# 2. Test public access removed
curl https://agent-service-staging.run.app/health
# Expected: 403 Forbidden

# 3. Test gateway can still reach service
curl -X POST https://gateway-staging.run.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"query": "{ conversations { id } }"}'
# Expected: GraphQL response (success)

# 4. Test service can access secrets
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=agent-service AND severity>=ERROR" \
  --limit=20
# Look for: "Failed to access secret" errors (should be none)

# 5. Test service functionality
# Run integration tests, verify database access, external API calls, etc.
```

---

## Validation Checklist

**Before marking IAM improvements complete**:

- [ ] All backend services reject unauthenticated requests (403)
- [ ] Gateway can successfully invoke all backend services
- [ ] Services can access ONLY their designated secrets
- [ ] Services cannot access other services' secrets
- [ ] Celery worker can invoke ONLY agent + journal services
- [ ] No project-level IAM bindings for services (except necessary infrastructure roles)
- [ ] `gcloud projects get-iam-policy` shows minimal service-level grants
- [ ] All integration tests pass
- [ ] Production deployment successful with no permission errors

---

## Rollback Plan

**If IAM changes break functionality**:

```bash
# Option 1: Restore public access temporarily
gcloud run services add-iam-policy-binding agent-service \
  --region=us-east4 \
  --project=mindmirror-staging \
  --member="allUsers" \
  --role="roles/run.invoker"

# Option 2: Revert Tofu changes
git revert <commit-hash>
tofu apply -var-file=staging.auto.tfvars

# Option 3: Grant project-level access temporarily
gcloud projects add-iam-policy-binding mindmirror-staging \
  --member="serviceAccount:agent-service@mindmirror-staging.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Then investigate and fix properly**

---

## Advanced: IAM Conditions

**Restrict by time or IP (optional)**:

```hcl
resource "google_cloud_run_v2_service_iam_member" "gateway_access_conditional" {
  location = google_cloud_run_v2_service.agent_service.location
  project  = google_cloud_run_v2_service.agent_service.project
  name     = google_cloud_run_v2_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.gateway.email}"

  # Only allow during business hours (optional)
  condition {
    title       = "business-hours-only"
    description = "Only allow access during business hours (debugging restriction)"
    expression  = "request.time.getHours('America/New_York') >= 9 && request.time.getHours('America/New_York') <= 17"
  }
}
```

**Note**: Not recommended for production (services should work 24/7), but useful for debugging or compliance

---

## Monitoring IAM Changes

**Cloud Audit Logs for IAM**:

```bash
# Monitor IAM policy changes
gcloud logging read \
  "protoPayload.methodName=SetIamPolicy AND resource.type=cloud_run_service" \
  --limit=50 \
  --format=json
```

**Alert on unauthorized access attempts**:

```hcl
resource "google_logging_metric" "unauthorized_cloud_run" {
  name   = "unauthorized_cloud_run_access"
  filter = "protoPayload.status.code=7 AND resource.type=\"cloud_run_revision\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_monitoring_alert_policy" "unauthorized_access" {
  display_name = "Unauthorized Cloud Run Access Attempts"
  combiner     = "OR"

  conditions {
    display_name = "Unauthorized access > 5/min"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/unauthorized_cloud_run_access\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5
    }
  }

  notification_channels = [google_monitoring_notification_channel.security_team.name]
}
```

---

## Best Practices Summary

1. ✅ **Never use `allUsers` for backend services** (gateway only)
2. ✅ **Use resource-level IAM** (not project-level) for secrets and services
3. ✅ **Grant minimum permissions** needed for functionality
4. ✅ **Document permissions matrix** (who needs what)
5. ✅ **Test incrementally** (one service at a time)
6. ✅ **Monitor IAM changes** (audit logs + alerts)
7. ✅ **Review quarterly** (remove unused permissions)

---

## References

- [IAM Best Practices](https://cloud.google.com/iam/docs/best-practices-for-using-and-managing-service-accounts)
- [Cloud Run IAM](https://cloud.google.com/run/docs/securing/managing-access)
- [Secret Manager IAM](https://cloud.google.com/secret-manager/docs/access-control)
- [Least Privilege Principle](https://cloud.google.com/iam/docs/using-iam-securely#least_privilege)
