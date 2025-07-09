resource "google_cloud_run_service" "journal_service" {
  name     = "journal-service"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = var.journal_service_container_image

        ports {
          container_port = 8000
        }

        # Non-secret env vars
        env {
          name  = "GCS_BUCKET_NAME"
          value = var.gcs_bucket_name
        }

        # GCS Configuration (Production)
        env {
          name  = "USE_GCS_EMULATOR"
          value = "false"
        }

        env {
          name  = "STORAGE_EMULATOR_HOST"
          value = ""  # Empty to disable emulator
        }

        env {
          name  = "TRADITION_DISCOVERY_MODE"
          value = "gcs-only"  # No local fallback
        }

        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }

        # Database Configuration
        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }

        # Redis Configuration
        env {
          name  = "REDIS_URL"
          value = var.redis_url
        }

        # Supabase Configuration
        env {
          name  = "SUPABASE_URL"
          value = var.supabase_url
        }

        env {
          name  = "SUPABASE_ANON_KEY"
          value = var.supabase_anon_key
        }

        env {
          name  = "SUPABASE_SERVICE_ROLE_KEY"
          value = var.supabase_service_role_key
        }

        env {
          name  = "SUPABASE_CA_CERT_PATH"
          value = var.supabase_ca_cert_path
        }

        # Container Configuration
        env {
          name  = "I_AM_IN_A_DOCKER_CONTAINER"
          value = "1"
        }

        env {
          name  = "FAUX_MESH_USER_ID"
          value = var.faux_mesh_user_id
        }

        env {
          name  = "FAUX_MESH_SUPABASE_ID"
          value = var.faux_mesh_supabase_id
        }

        env {
          name  = "LOG_LEVEL"
          value = var.log_level
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DEBUG"
          value = var.debug
        }

        env {
          name  = "AGENT_SERVICE_URL"
          value = var.agent_service_url
        }

        env {
          name  = "CELERY_WORKER_URL"
          value = var.celery_worker_url
        }

        env {
          name  = "REINDEX_SECRET_KEY"
          value = var.reindex_secret_key
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

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.journal_service.location
  project  = google_cloud_run_service.journal_service.project
  service  = google_cloud_run_service.journal_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

