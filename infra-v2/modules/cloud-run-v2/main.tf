# Reusable Cloud Run v2 Module
# This module creates a Cloud Run v2 service with:
# - Secret volume mounts (more secure than env vars)
# - Health checks (startup + liveness probes)
# - Configurable scaling (min/max instances)
# - IAM configuration (public vs internal)

resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    # Scaling configuration
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # Service account
    service_account = var.service_account_email

    # Secret volumes
    dynamic "volumes" {
      for_each = var.secret_volumes
      content {
        name = volumes.value.volume_name
        secret {
          secret = volumes.value.secret_name
          items {
            version = "latest"
            path    = volumes.value.filename
          }
        }
      }
    }

    containers {
      image = var.image

      ports {
        container_port = var.port
      }

      # Mount secret volumes
      dynamic "volume_mounts" {
        for_each = var.secret_volumes
        content {
          name       = volume_mounts.value.volume_name
          mount_path = "/secrets/${volume_mounts.value.volume_name}"
        }
      }

      # Environment variables (non-secret config only)
      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.value.name
          value = env.value.value
        }
      }

      # Startup probe (gives service time to boot)
      startup_probe {
        http_get {
          path = var.health_check_path
          port = var.port
        }
        initial_delay_seconds = var.startup_probe_initial_delay
        timeout_seconds       = var.startup_probe_timeout
        period_seconds        = var.startup_probe_period
        failure_threshold     = var.startup_probe_failure_threshold
      }

      # Liveness probe (checks if service is healthy)
      liveness_probe {
        http_get {
          path = var.health_check_path
          port = var.port
        }
        initial_delay_seconds = 0
        timeout_seconds       = 3
        period_seconds        = 30
        failure_threshold     = 3
      }

      # Resource limits
      resources {
        limits = {
          cpu    = var.cpu_limit
          memory = var.memory_limit
        }
      }
    }
  }

  # Ingress control (all or internal-only)
  ingress = var.ingress

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# IAM - Public access (conditional)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.allow_unauthenticated ? 1 : 0

  project  = google_cloud_run_v2_service.service.project
  location = google_cloud_run_v2_service.service.location
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
