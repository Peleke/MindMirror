# Cloud Run v2 - Practices Service
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

resource "google_cloud_run_v2_service" "practices" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    # Service account
    service_account = var.service_account_email

    # Scaling configuration
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    # Container configuration
    containers {
      image = var.image

      ports {
        name           = "http1"
        container_port = 8000
      }

      # Resource limits (v2 uses millicpu notation)
      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = false
      }

      # Environment variables
      env {
        name  = "API_VERSION"
        value = "0.1.0"
      }

      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }

      # Dynamic environment variables from var.env
      dynamic "env" {
        for_each = var.env
        content {
          name  = env.key
          value = env.value
        }
      }

      # Health probes (configurable)
      dynamic "startup_probe" {
        for_each = var.enable_health_probes ? [1] : []
        content {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 10
          timeout_seconds       = 3
          period_seconds        = 10
          failure_threshold     = 3
        }
      }

      dynamic "liveness_probe" {
        for_each = var.enable_health_probes ? [1] : []
        content {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 30
          timeout_seconds       = 3
          period_seconds        = 30
          failure_threshold     = 3
        }
      }
    }

    # Max concurrent requests per instance
    max_instance_request_concurrency = 20

    # Request timeout
    timeout = "300s"
  }

  # Traffic routing
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Labels
  labels = {
    managed-by = "terraform"
    service    = "practices"
    env        = var.environment
  }
}

# IAM - Public access
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.practices.location
  project  = google_cloud_run_v2_service.practices.project
  name     = google_cloud_run_v2_service.practices.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output
output "service_url" {
  value = google_cloud_run_v2_service.practices.uri
}
