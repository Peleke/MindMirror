resource "google_cloud_run_service" "habits_service" {
  name     = "habits-service"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = var.habits_service_container_image

        ports { container_port = 8003 }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        env {
          name  = "LOG_LEVEL"
          value = var.log_level
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
  location = google_cloud_run_service.habits_service.location
  project  = google_cloud_run_service.habits_service.project
  service  = google_cloud_run_service.habits_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}


