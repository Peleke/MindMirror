# Cloud Run v2 Migration Guide

## Why Migrate to v2?

Cloud Run v2 (based on Knative v1) provides:

✅ **Volume mounts** - Mount secrets as files (required for your volume mount strategy)
✅ **Better resource controls** - CPU throttling, startup CPU boost
✅ **Health probes** - Startup, liveness, readiness probes
✅ **Direct secret references** - Reference Secret Manager without manual env vars
✅ **Improved scaling** - Better min/max instance controls
✅ **VPC egress control** - More granular network configuration

## Difficulty Assessment: **EASY** ⭐

The migration is straightforward because:
- Same underlying Cloud Run infrastructure
- Similar Terraform structure (just flatter/cleaner)
- No data migration needed (stateless services)
- Can test with `-auto` parallel stack before touching production

## Migration Complexity by Service

| Service | Difficulty | Reason |
|---------|------------|--------|
| `practices_service` | ⭐ Easy | Simple service, no complex dependencies |
| `movements_service` | ⭐ Easy | Similar to practices |
| `users_service` | ⭐ Easy | Similar structure |
| `meals_service` | ⭐ Easy | Minimal config |
| `journal_service` | ⭐⭐ Medium | More env vars, dependencies |
| `agent_service` | ⭐⭐ Medium | More complex config |
| `habits_service` | ⭐⭐ Medium | Multiple dependencies |
| `gateway` | ⭐⭐⭐ Complex | Critical path, routing logic |
| `celery_worker` | ⭐⭐⭐ Complex | Pub/Sub integration, multiple topics |

**Recommendation**: Start with `practices_service` (simplest), validate, then roll out to others.

## Key Changes: v1 → v2

### 1. Resource Name
```hcl
# v1
resource "google_cloud_run_service" "practices" { }

# v2
resource "google_cloud_run_v2_service" "practices" { }
```

### 2. Provider Version
```hcl
# v1 (old)
version = ">= 4.0"

# v2 (required)
version = ">= 5.0"
```

### 3. Structure Flattening
```hcl
# v1 (nested)
template {
  spec {
    containers { }
  }
}

# v2 (flatter)
template {
  containers { }
}
```

### 4. CPU Format
```hcl
# v1
cpu = "1"

# v2
cpu = "1000m"  # Millicpu notation
```

### 5. Volume Mounts (NEW!)
```hcl
# v2 only - mount secrets as files
template {
  volumes {
    name = "secrets-volume"
    secret {
      secret = "DATABASE_URL"
      items {
        version = "latest"
        path    = "db_url"
      }
    }
  }

  containers {
    volume_mounts {
      name       = "secrets-volume"
      mount_path = "/secrets"  # File available at /secrets/db_url
    }
  }
}
```

### 6. Secret References (NEW!)
```hcl
# v1 - must pass as plain env var
env {
  name  = "DATABASE_URL"
  value = var.database_url  # Exposed in plan/state
}

# v2 - direct Secret Manager reference
env {
  name = "DATABASE_URL"
  value_source {
    secret_key_ref {
      secret  = "DATABASE_URL"
      version = "latest"
    }
  }
}
```

### 7. Health Probes (NEW!)
```hcl
# v2 only
containers {
  startup_probe {
    http_get {
      path = "/health"
      port = 8000
    }
    initial_delay_seconds = 10
    failure_threshold     = 3
  }

  liveness_probe {
    http_get {
      path = "/health"
    }
    period_seconds = 30
  }
}
```

### 8. Scaling
```hcl
# v1
metadata {
  annotations = {
    "autoscaling.knative.dev/minScale" = "1"
    "autoscaling.knative.dev/maxScale" = "10"
  }
}

# v2
template {
  scaling {
    min_instance_count = 1
    max_instance_count = 10
  }
}
```

### 9. IAM Resource Reference
```hcl
# v1
resource "google_cloud_run_service_iam_member" "public" {
  service = google_cloud_run_service.practices.name
}

# v2
resource "google_cloud_run_v2_service_iam_member" "public" {
  name = google_cloud_run_v2_service.practices.name
}
```

## Migration Strategy

### Phase 1: Practices Service (Test Case)

1. **Backup current config**:
```bash
cp infra/modules/practices/main.tf infra/modules/practices/main.v1.tf.backup
```

2. **Update main.tf** with v2 resource (see `main_v2.tf.example`)

3. **Test with -auto stack**:
```bash
cd infra
tofu plan -var-file=staging.auto.tfvars -target=module.practices_service
# Should show: practices-service-auto will be created (v2)
```

4. **Apply and validate**:
```bash
tofu apply -var-file=staging.auto.tfvars -target=module.practices_service

# Test the service
curl https://practices-service-auto-[hash].run.app/health
```

5. **If successful**, verify:
   - Service responds correctly
   - Environment variables work
   - Database connections work
   - No errors in logs

### Phase 2: Add Volume Mounts

Once v2 is working, add secrets as volume mounts:

```hcl
template {
  volumes {
    name = "app-secrets"
    secret {
      secret = "PRACTICES_SERVICE_SECRETS"  # Create this in Secret Manager
      items {
        version = "latest"
        path    = "config.json"
      }
    }
  }

  containers {
    volume_mounts {
      name       = "app-secrets"
      mount_path = "/etc/secrets"
    }

    # Application can now read from /etc/secrets/config.json
    env {
      name  = "SECRETS_PATH"
      value = "/etc/secrets/config.json"
    }
  }
}
```

### Phase 3: Roll Out to Other Services

After practices_service is validated:
1. Movements, users, meals (simple services)
2. Journal, agent, habits (medium complexity)
3. Gateway, celery-worker (complex - do last)

## Variables to Add

For volume mount support, add to `variables.tf`:

```hcl
variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  default     = "staging"
}

variable "secrets_volume_name" {
  description = "Secret Manager secret name for volume mount"
  type        = string
  default     = ""  # Empty = don't mount secrets
}

variable "secrets_mount_path" {
  description = "Path to mount secrets volume"
  type        = string
  default     = "/secrets"
}

variable "enable_health_probes" {
  description = "Enable startup/liveness probes"
  type        = bool
  default     = true
}
```

## Testing Checklist

For each migrated service:

- [ ] Service deploys successfully
- [ ] Health endpoint responds (if configured)
- [ ] Environment variables accessible
- [ ] Database connections work
- [ ] API endpoints return expected responses
- [ ] No errors in Cloud Run logs
- [ ] Metrics/monitoring still working
- [ ] IAM permissions correct (public/private access)

## Rollback Plan

If issues occur:

```bash
# Option 1: Keep old v1 service running, fix v2 issues
# The -auto service is separate, so old service unaffected

# Option 2: Revert Terraform config
cp infra/modules/practices/main.v1.tf.backup infra/modules/practices/main.tf
tofu plan  # Should show reverting to v1

# Option 3: Manual rollback
gcloud run services delete practices-service-auto \
  --region=us-east4 \
  --project=mindmirror-69
```

## Benefits After Migration

1. **Security**: Secrets never exposed in Terraform state/plans
2. **Flexibility**: Can mount multiple secrets as files
3. **Reliability**: Health probes catch issues faster
4. **Performance**: Better resource controls and CPU throttling
5. **Observability**: Better metrics and monitoring
6. **Modern**: v2 is the recommended API going forward

## Timeline Estimate

- **Practices service migration**: 1-2 hours (including testing)
- **Simple services (3)**: 2-3 hours
- **Medium services (3)**: 3-4 hours
- **Complex services (2)**: 4-6 hours
- **Total**: ~10-15 hours spread over multiple days

## References

- [Cloud Run v2 API Migration Guide](https://cloud.google.com/run/docs/migrating)
- [Terraform google_cloud_run_v2_service](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service)
- [Secrets as Volume Mounts](https://cloud.google.com/run/docs/configuring/secrets#mounting-secrets)
