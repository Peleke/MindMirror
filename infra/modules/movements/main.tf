terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
}

resource "google_cloud_run_service" "movements" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
      }
    }

    spec {
      container_concurrency = 20
      containers {
        image = var.image

        ports {
          container_port = 8000
        }

        # Static port env for Cloud Run
        env {
          name  = "MOVEMENTS_HTTP_PORT"
          value = "8000"
        }

        # Database Configuration
        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }

        # DB pool tuning
        env {
          name  = "DB_POOL_SIZE"
          value = "10"
        }
        env {
          name  = "DB_MAX_OVERFLOW"
          value = "20"
        }
        env {
          name  = "DB_POOL_TIMEOUT"
          value = "10"
        }
        env {
          name  = "DB_POOL_RECYCLE"
          value = "1800"
        }

        # Plain env vars from map
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
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.movements.location
  project  = google_cloud_run_service.movements.project
  service  = google_cloud_run_service.movements.name
  role     = "roles/run.invoker"
  member   = "allUsers"
} 