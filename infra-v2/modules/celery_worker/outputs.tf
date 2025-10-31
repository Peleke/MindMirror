output "service_url" {
  description = "Celery worker URL"
  value       = module.celery_worker.service_url
}

output "service_name" {
  description = "Celery worker service name"
  value       = module.celery_worker.service_name
}

output "service_account_email" {
  description = "Celery worker service account email"
  value       = google_service_account.celery_worker.email
}

# Pub/Sub Topics
output "journal_indexing_topic" {
  description = "Journal indexing Pub/Sub topic"
  value       = google_pubsub_topic.journal_indexing.name
}

output "journal_batch_indexing_topic" {
  description = "Journal batch indexing Pub/Sub topic"
  value       = google_pubsub_topic.journal_batch_indexing.name
}

output "journal_reindex_topic" {
  description = "Journal reindex Pub/Sub topic"
  value       = google_pubsub_topic.journal_reindex.name
}

output "tradition_rebuild_topic" {
  description = "Tradition rebuild Pub/Sub topic"
  value       = google_pubsub_topic.tradition_rebuild.name
}

output "health_check_topic" {
  description = "Health check Pub/Sub topic"
  value       = google_pubsub_topic.health_check.name
}
