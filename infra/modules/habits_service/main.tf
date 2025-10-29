resource "google_cloud_run_service" "habits_service" {
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
        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        # DB pool tuning (uses app defaults if not overridden)
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
        env {
          name  = "DB_POOL_PRE_PING"
          value = "true"
        }
        env {
          name  = "VOUCHERS_WEB_BASE_URL"
          value = var.vouchers_web_base_url
        }
        env {
          name  = "UYE_PROGRAM_TEMPLATE_ID"
          value = var.uye_program_template_id
        }
        env {
          name  = "MINDMIRROR_PROGRAM_TEMPLATE_ID"
          value = var.mindmirror_program_template_id
        }

        env {
          name  = "DAILY_JOURNALING_PROGRAM_TEMPLATE_ID"
          value = var.daily_journaling_program_template_id
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

resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.habits_service.location
  project  = google_cloud_run_service.habits_service.project
  service  = google_cloud_run_service.habits_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
