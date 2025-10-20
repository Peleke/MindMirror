output "traditions_bucket_name" {
  description = "GCS bucket name for traditions storage"
  value       = google_storage_bucket.traditions.name
}

output "agent_service_sa_email" {
  description = "Agent service service account email"
  value       = google_service_account.agent_service.email
}

output "journal_service_sa_email" {
  description = "Journal service service account email"
  value       = google_service_account.journal_service.email
}

output "meals_service_sa_email" {
  description = "Meals service service account email"
  value       = google_service_account.meals_service.email
}

output "movements_service_sa_email" {
  description = "Movements service service account email"
  value       = google_service_account.movements_service.email
}

output "practices_service_sa_email" {
  description = "Practices service service account email"
  value       = google_service_account.practices_service.email
}

output "users_service_sa_email" {
  description = "Users service service account email"
  value       = google_service_account.users_service.email
}
