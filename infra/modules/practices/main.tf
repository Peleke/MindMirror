terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
}

resource "google_cloud_run_service" "practices" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    spec {
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
}

resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.practices.location
  project  = google_cloud_run_service.practices.project
  service  = google_cloud_run_service.practices.name
  role     = "roles/run.invoker"
  member   = "allUsers"
} 