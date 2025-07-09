resource "google_cloud_run_service" "celery_worker" {
  name     = "celery-worker"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = var.celery_worker_container_image

        ports {
          container_port = 8000
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

        # Qdrant Configuration
        env {
          name  = "QDRANT_URL"
          value = var.qdrant_url
        }

        env {
          name  = "QDRANT_API_KEY"
          value = var.qdrant_api_key
        }

        # OpenAI Configuration
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }

        # Embedding Configuration
        env {
          name  = "EMBEDDING_SERVICE"
          value = "openai"
        }

        env {
          name  = "EMBEDDING_MODEL"
          value = "text-embedding-3-small"
        }

        env {
          name  = "EMBEDDING_VECTOR_SIZE"
          value = "768"
        }

        # Service URLs
        env {
          name  = "JOURNAL_SERVICE_URL"
          value = var.journal_service_url
        }

        env {
          name  = "AGENT_SERVICE_URL"
          value = var.agent_service_url
        }

        # Security
        env {
          name  = "REINDEX_SECRET_KEY"
          value = var.reindex_secret_key
        }

        # Task Configuration
        env {
          name  = "TASK_DEFAULT_RETRY_DELAY"
          value = "60"
        }

        env {
          name  = "TASK_MAX_RETRIES"
          value = "3"
        }

        env {
          name  = "TASK_TIME_LIMIT"
          value = "300"
        }

        # Environment
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DEBUG"
          value = var.debug
        }

        env {
          name  = "TESTING"
          value = "false"
        }
      }

      service_account_name = google_service_account.celery_worker.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Data sources for service accounts from base module
data "google_service_account" "journal_service" {
  account_id = "journal-service"
  project    = var.project_id
}

data "google_service_account" "agent_service" {
  account_id = "agent-service"
  project    = var.project_id
}

# Service account for celery worker
resource "google_service_account" "celery_worker" {
  account_id   = "celery-worker"
  display_name = "Service Account for Celery Worker"
  project      = var.project_id
}

# Secret Manager access for celery worker
resource "google_project_iam_member" "celery_worker_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}

# Cloud Run invoker access for celery worker
resource "google_project_iam_member" "celery_worker_sa_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}

# Allow journal service to invoke celery worker
resource "google_cloud_run_service_iam_member" "journal_service_invoker" {
  location = google_cloud_run_service.celery_worker.location
  project  = google_cloud_run_service.celery_worker.project
  service  = google_cloud_run_service.celery_worker.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${data.google_service_account.journal_service.email}"
}

# Allow agent service to invoke celery worker
resource "google_cloud_run_service_iam_member" "agent_service_invoker" {
  location = google_cloud_run_service.celery_worker.location
  project  = google_cloud_run_service.celery_worker.project
  service  = google_cloud_run_service.celery_worker.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${data.google_service_account.agent_service.email}"
} 