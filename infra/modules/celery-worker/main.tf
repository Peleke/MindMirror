# Pub/Sub Topics
resource "google_pubsub_topic" "journal_indexing" {
  name    = "journal-indexing"
  project = var.project_id
}

resource "google_pubsub_topic" "journal_batch_indexing" {
  name    = "journal-batch-indexing"
  project = var.project_id
}

resource "google_pubsub_topic" "journal_reindex" {
  name    = "journal-reindex"
  project = var.project_id
}

resource "google_pubsub_topic" "tradition_rebuild" {
  name    = "tradition-rebuild"
  project = var.project_id
}

resource "google_pubsub_topic" "health_check" {
  name    = "health-check"
  project = var.project_id
}

# Dead Letter Topics
resource "google_pubsub_topic" "journal_indexing_dlq" {
  name    = "journal-indexing-dlq"
  project = var.project_id
}

resource "google_pubsub_topic" "journal_batch_indexing_dlq" {
  name    = "journal-batch-indexing-dlq"
  project = var.project_id
}

resource "google_pubsub_topic" "journal_reindex_dlq" {
  name    = "journal-reindex-dlq"
  project = var.project_id
}

resource "google_pubsub_topic" "tradition_rebuild_dlq" {
  name    = "tradition-rebuild-dlq"
  project = var.project_id
}

resource "google_pubsub_topic" "health_check_dlq" {
  name    = "health-check-dlq"
  project = var.project_id
}

# Pub/Sub Push Subscriptions
resource "google_pubsub_subscription" "journal_indexing_sub" {
  name    = "journal-indexing-sub"
  topic   = google_pubsub_topic.journal_indexing.name
  project = var.project_id

  # Push configuration - messages will be pushed to Cloud Run service
  push_config {
    push_endpoint = "https://celery-worker-web-${var.project_numerical_id}.${var.region}.run.app/pubsub/journal-indexing"
    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }

  # Dead letter configuration
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.journal_indexing_dlq.id
    max_delivery_attempts = 5
  }

  # Message retention
  message_retention_duration = "604800s"  # 7 days
}

resource "google_pubsub_subscription" "journal_batch_indexing_sub" {
  name    = "journal-batch-indexing-sub"
  topic   = google_pubsub_topic.journal_batch_indexing.name
  project = var.project_id

  push_config {
    push_endpoint = "https://celery-worker-web-${var.project_numerical_id}.${var.region}.run.app/pubsub/journal-batch-indexing"
    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.journal_batch_indexing_dlq.id
    max_delivery_attempts = 5
  }

  message_retention_duration = "604800s"
}

resource "google_pubsub_subscription" "journal_reindex_sub" {
  name    = "journal-reindex-sub"
  topic   = google_pubsub_topic.journal_reindex.name
  project = var.project_id

  push_config {
    push_endpoint = "https://celery-worker-web-${var.project_numerical_id}.${var.region}.run.app/pubsub/journal-reindex"
    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.journal_reindex_dlq.id
    max_delivery_attempts = 5
  }

  message_retention_duration = "604800s"
}

resource "google_pubsub_subscription" "tradition_rebuild_sub" {
  name    = "tradition-rebuild-sub"
  topic   = google_pubsub_topic.tradition_rebuild.name
  project = var.project_id

  push_config {
    push_endpoint = "https://celery-worker-web-${var.project_numerical_id}.${var.region}.run.app/pubsub/tradition-rebuild"
    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.tradition_rebuild_dlq.id
    max_delivery_attempts = 5
  }

  message_retention_duration = "604800s"
}

resource "google_pubsub_subscription" "health_check_sub" {
  name    = "health-check-sub"
  topic   = google_pubsub_topic.health_check.name
  project = var.project_id

  push_config {
    push_endpoint = "https://celery-worker-web-${var.project_numerical_id}.${var.region}.run.app/pubsub/health-check"
    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
    attributes = {
      x-goog-version = "v1"
    }
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.health_check_dlq.id
    max_delivery_attempts = 5
  }

  message_retention_duration = "604800s"
}

# Cloud Run Services
resource "google_cloud_run_service" "celery_worker_web" {
  name     = "celery-worker-web"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = var.celery_worker_container_image
        command = ["./start-web.sh"]

        ports {
          container_port = 8000
        }

        # Run mode
        env {
          name  = "RUN_MODE"
          value = "web"
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
          value = "1536"
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

        # Pub/Sub Topics
        env {
          name  = "JOURNAL_INDEXING_TOPIC"
          value = google_pubsub_topic.journal_indexing.name
        }

        env {
          name  = "JOURNAL_BATCH_INDEXING_TOPIC"
          value = google_pubsub_topic.journal_batch_indexing.name
        }

        env {
          name  = "JOURNAL_REINDEX_TOPIC"
          value = google_pubsub_topic.journal_reindex.name
        }

        env {
          name  = "TRADITION_REBUILD_TOPIC"
          value = google_pubsub_topic.tradition_rebuild.name
        }

        env {
          name  = "HEALTH_CHECK_TOPIC"
          value = google_pubsub_topic.health_check.name
        }

        # Pub/Sub Subscriptions
        env {
          name  = "JOURNAL_INDEXING_SUBSCRIPTION"
          value = google_pubsub_subscription.journal_indexing_sub.name
        }

        env {
          name  = "JOURNAL_BATCH_INDEXING_SUBSCRIPTION"
          value = google_pubsub_subscription.journal_batch_indexing_sub.name
        }

        env {
          name  = "JOURNAL_REINDEX_SUBSCRIPTION"
          value = google_pubsub_subscription.journal_reindex_sub.name
        }

        env {
          name  = "TRADITION_REBUILD_SUBSCRIPTION"
          value = google_pubsub_subscription.tradition_rebuild_sub.name
        }

        env {
          name  = "HEALTH_CHECK_SUBSCRIPTION"
          value = google_pubsub_subscription.health_check_sub.name
        }

        # Google Cloud Project ID
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
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

# Allow unauthenticated access to the Cloud Run web service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.celery_worker_web.location
  project  = google_cloud_run_service.celery_worker_web.project
  service  = google_cloud_run_service.celery_worker_web.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Allow journal service to invoke celery_worker_web
resource "google_cloud_run_service_iam_member" "journal_service_invoker_web" {
  location = google_cloud_run_service.celery_worker_web.location
  project  = google_cloud_run_service.celery_worker_web.project
  service  = google_cloud_run_service.celery_worker_web.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${data.google_service_account.journal_service.email}"
}

# Allow agent service to invoke celery_worker_web
resource "google_cloud_run_service_iam_member" "agent_service_invoker_web" {
  location = google_cloud_run_service.celery_worker_web.location
  project  = google_cloud_run_service.celery_worker_web.project
  service  = google_cloud_run_service.celery_worker_web.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${data.google_service_account.agent_service.email}"
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

# Pub/Sub Publisher permissions for celery worker
resource "google_project_iam_member" "celery_worker_sa_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}

# Pub/Sub Subscriber permissions for celery worker
resource "google_project_iam_member" "celery_worker_sa_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}

# Pub/Sub Viewer permissions for celery worker (to list topics/subscriptions)
resource "google_project_iam_member" "celery_worker_sa_pubsub_viewer" {
  project = var.project_id
  role    = "roles/pubsub.viewer"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}

# Allow journal service to invoke celery worker
resource "google_cloud_run_service_iam_member" "journal_service_invoker" {
  location = google_cloud_run_service.celery_worker_web.location
  project  = google_cloud_run_service.celery_worker_web.project
  service  = google_cloud_run_service.celery_worker_web.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${data.google_service_account.journal_service.email}"
}

# Allow agent service to invoke celery worker
resource "google_cloud_run_service_iam_member" "agent_service_invoker" {
  location = google_cloud_run_service.celery_worker_web.location
  project  = google_cloud_run_service.celery_worker_web.project
  service  = google_cloud_run_service.celery_worker_web.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${data.google_service_account.agent_service.email}"
} 