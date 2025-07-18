output "celery_worker_url" {
  description = "Celery worker web service URL (handles both HTTP API and Pub/Sub push messages)"
  value       = google_cloud_run_service.celery_worker_web.status[0].url
}

output "celery_worker_service_account_email" {
  description = "Celery worker service account email"
  value       = google_service_account.celery_worker.email
}

# Pub/Sub Topic Outputs
output "journal_indexing_topic" {
  description = "Journal indexing topic name"
  value       = google_pubsub_topic.journal_indexing.name
}

output "journal_batch_indexing_topic" {
  description = "Journal batch indexing topic name"
  value       = google_pubsub_topic.journal_batch_indexing.name
}

output "journal_reindex_topic" {
  description = "Journal reindex topic name"
  value       = google_pubsub_topic.journal_reindex.name
}

output "tradition_rebuild_topic" {
  description = "Tradition rebuild topic name"
  value       = google_pubsub_topic.tradition_rebuild.name
}

output "health_check_topic" {
  description = "Health check topic name"
  value       = google_pubsub_topic.health_check.name
}

# Pub/Sub Subscription Outputs
output "journal_indexing_subscription" {
  description = "Journal indexing subscription name"
  value       = google_pubsub_subscription.journal_indexing_sub.name
}

output "journal_batch_indexing_subscription" {
  description = "Journal batch indexing subscription name"
  value       = google_pubsub_subscription.journal_batch_indexing_sub.name
}

output "journal_reindex_subscription" {
  description = "Journal reindex subscription name"
  value       = google_pubsub_subscription.journal_reindex_sub.name
}

output "tradition_rebuild_subscription" {
  description = "Tradition rebuild subscription name"
  value       = google_pubsub_subscription.tradition_rebuild_sub.name
}

output "health_check_subscription" {
  description = "Health check subscription name"
  value       = google_pubsub_subscription.health_check_sub.name
}

# Dead Letter Topic Outputs
output "journal_indexing_dlq_topic" {
  description = "Journal indexing dead letter topic name"
  value       = google_pubsub_topic.journal_indexing_dlq.name
}

output "journal_batch_indexing_dlq_topic" {
  description = "Journal batch indexing dead letter topic name"
  value       = google_pubsub_topic.journal_batch_indexing_dlq.name
}

output "journal_reindex_dlq_topic" {
  description = "Journal reindex dead letter topic name"
  value       = google_pubsub_topic.journal_reindex_dlq.name
}

output "tradition_rebuild_dlq_topic" {
  description = "Tradition rebuild dead letter topic name"
  value       = google_pubsub_topic.tradition_rebuild_dlq.name
}

output "health_check_dlq_topic" {
  description = "Health check dead letter topic name"
  value       = google_pubsub_topic.health_check_dlq.name
} 