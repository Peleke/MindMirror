resource "google_cloud_run_service" "agent_service" {
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
        image = var.agent_service_container_image

        ports {
          container_port = 8000
        }

        # GCS Configuration
        env {
          name  = "GCS_BUCKET_NAME"
          value = var.gcs_bucket_name
        }

        env {
          name  = "PROMPT_STORAGE_TYPE"
          value = "gcs"
        }

        env {
          name  = "YAML_STORAGE_PATH"
          value = "/app/prompts"
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

        # Vector Database Configuration
        env {
          name  = "QDRANT_URL"
          value = var.qdrant_url
        }

        env {
          name  = "QDRANT_API_KEY"
          value = var.qdrant_api_key
        }

        # LLM Configuration
        env {
          name  = "LLM_PROVIDER"
          value = "openai"
        }

        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }

        env {
          name  = "OPENAI_MODEL"
          value = "gpt-4o-mini"
        }

        env {
          name  = "EMBEDDING_PROVIDER"
          value = "openai"
        }

        env {
          name  = "EMBEDDING_MODEL"
          value = "text-embedding-3-small"
        }

        env {
          name  = "EMBEDDING_VECTOR_SIZE"
          value = "1536"
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

        # Service URLs
        env {
          name  = "CELERY_WORKER_URL"
          value = var.celery_worker_url
        }

        env {
          name  = "JOURNAL_SERVICE_URL"
          value = var.journal_service_url
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
  location = google_cloud_run_service.agent_service.location
  project  = google_cloud_run_service.agent_service.project
  service  = google_cloud_run_service.agent_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "agent_service_url" {
  value = google_cloud_run_service.agent_service.status[0].url
}

