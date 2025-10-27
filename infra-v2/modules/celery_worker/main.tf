# Celery Worker - Cloud Run v2
# Background task processing (journal indexing, knowledge base building)

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

# Service Account for Celery Worker
resource "google_service_account" "celery_worker" {
  account_id   = "celery-worker"
  display_name = "Celery Worker Service Account"
  project      = var.project_id
}

# IAM Permissions
resource "google_project_iam_member" "celery_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
}

resource "google_pubsub_topic_iam_member" "celery_publisher" {
  for_each = toset([
    google_pubsub_topic.journal_indexing.id,
    google_pubsub_topic.journal_batch_indexing.id,
    google_pubsub_topic.journal_reindex.id,
    google_pubsub_topic.tradition_rebuild.id,
    google_pubsub_topic.health_check.id,
  ])

  topic   = each.value
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.celery_worker.email}"
  project = var.project_id
}

# Cloud Run Service
module "celery_worker" {
  source = "../cloud-run-v2"

  project_id            = var.project_id
  region                = var.region
  service_name          = "celery-worker"
  image                 = var.image
  service_account_email = google_service_account.celery_worker.email

  # Background worker (cold starts acceptable)
  min_instances = var.min_instances
  max_instances = var.max_instances

  # Secret volumes
  secret_volumes = [
    {
      volume_name = "database-url"
      secret_name = var.database_url_secret
      filename    = "database-url"
    },
    {
      volume_name = "redis-url"
      secret_name = var.redis_url_secret
      filename    = "redis-url"
    },
    {
      volume_name = "qdrant-url"
      secret_name = var.qdrant_url_secret
      filename    = "qdrant-url"
    },
    {
      volume_name = "qdrant-api-key"
      secret_name = var.qdrant_api_key_secret
      filename    = "qdrant-api-key"
    },
    {
      volume_name = "openai-api-key"
      secret_name = var.openai_api_key_secret
      filename    = "openai-api-key"
    },
    {
      volume_name = "reindex-secret-key"
      secret_name = var.reindex_secret_key_secret
      filename    = "reindex-secret-key"
    },
  ]

  # Environment variables
  env_vars = [
    {
      name  = "ENVIRONMENT"
      value = var.environment
    },
    {
      name  = "DEBUG"
      value = tostring(var.debug)
    },
    {
      name  = "PORT"
      value = "8000"
    },
    {
      name  = "GOOGLE_CLOUD_PROJECT"
      value = var.project_id
    },
    # Celery configuration
    {
      name  = "RUN_MODE"
      value = "web"
    },
    {
      name  = "TESTING"
      value = "false"
    },
    # Embedding configuration
    {
      name  = "EMBEDDING_SERVICE"
      value = "openai"
    },
    {
      name  = "EMBEDDING_MODEL"
      value = "text-embedding-3-small"
    },
    {
      name  = "EMBEDDING_VECTOR_SIZE"
      value = "1536"
    },
    # Task configuration
    {
      name  = "TASK_DEFAULT_RETRY_DELAY"
      value = "60"
    },
    {
      name  = "TASK_MAX_RETRIES"
      value = "3"
    },
    {
      name  = "TASK_TIME_LIMIT"
      value = "300"
    },
    # Pub/Sub Topics
    {
      name  = "JOURNAL_INDEXING_TOPIC"
      value = google_pubsub_topic.journal_indexing.name
    },
    {
      name  = "JOURNAL_BATCH_INDEXING_TOPIC"
      value = google_pubsub_topic.journal_batch_indexing.name
    },
    {
      name  = "JOURNAL_REINDEX_TOPIC"
      value = google_pubsub_topic.journal_reindex.name
    },
    {
      name  = "TRADITION_REBUILD_TOPIC"
      value = google_pubsub_topic.tradition_rebuild.name
    },
    {
      name  = "HEALTH_CHECK_TOPIC"
      value = google_pubsub_topic.health_check.name
    },
    # Service URLs
    {
      name  = "JOURNAL_SERVICE_URL"
      value = var.journal_service_url
    },
    {
      name  = "AGENT_SERVICE_URL"
      value = var.agent_service_url
    },
  ]

  # Networking
  port                  = 8000
  ingress               = "INGRESS_TRAFFIC_ALL"
  allow_unauthenticated = false # Push subscriptions don't need public access

  # Health checks
  health_check_path = "/health"

  # Resources
  cpu_limit    = var.cpu_limit
  memory_limit = var.memory_limit
}

# Pub/Sub Push Subscriptions
resource "google_pubsub_subscription" "journal_indexing_sub" {
  name    = "journal-indexing-sub"
  topic   = google_pubsub_topic.journal_indexing.name
  project = var.project_id

  push_config {
    push_endpoint = "${module.celery_worker.service_url}/pubsub/journal-indexing"

    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
  }

  ack_deadline_seconds       = 60
  message_retention_duration = "604800s" # 7 days
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.journal_indexing.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_subscription" "journal_batch_indexing_sub" {
  name    = "journal-batch-indexing-sub"
  topic   = google_pubsub_topic.journal_batch_indexing.name
  project = var.project_id

  push_config {
    push_endpoint = "${module.celery_worker.service_url}/pubsub/journal-batch-indexing"

    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
  }

  ack_deadline_seconds       = 600
  message_retention_duration = "604800s"
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.journal_batch_indexing.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_subscription" "journal_reindex_sub" {
  name    = "journal-reindex-sub"
  topic   = google_pubsub_topic.journal_reindex.name
  project = var.project_id

  push_config {
    push_endpoint = "${module.celery_worker.service_url}/pubsub/journal-reindex"

    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
  }

  ack_deadline_seconds       = 600
  message_retention_duration = "604800s"
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.journal_reindex.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_subscription" "tradition_rebuild_sub" {
  name    = "tradition-rebuild-sub"
  topic   = google_pubsub_topic.tradition_rebuild.name
  project = var.project_id

  push_config {
    push_endpoint = "${module.celery_worker.service_url}/pubsub/tradition-rebuild"

    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
  }

  ack_deadline_seconds       = 600
  message_retention_duration = "604800s"
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.tradition_rebuild.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_subscription" "health_check_sub" {
  name    = "health-check-sub"
  topic   = google_pubsub_topic.health_check.name
  project = var.project_id

  push_config {
    push_endpoint = "${module.celery_worker.service_url}/pubsub/health-check"

    oidc_token {
      service_account_email = google_service_account.celery_worker.email
    }
  }

  ack_deadline_seconds       = 30
  message_retention_duration = "604800s"
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

# Grant invoker role to Pub/Sub
resource "google_cloud_run_v2_service_iam_member" "pubsub_invoker" {
  project  = var.project_id
  location = var.region
  name     = module.celery_worker.service_name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.celery_worker.email}"
}
