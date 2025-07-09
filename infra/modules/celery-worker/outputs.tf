output "celery_worker_url" {
  description = "Celery worker service URL"
  value       = google_cloud_run_service.celery_worker.status[0].url
}

output "celery_worker_service_account_email" {
  description = "Celery worker service account email"
  value       = google_service_account.celery_worker.email
} 