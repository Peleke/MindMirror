output "journal_service_url" {
  description = "Journal service Cloud Run URL"
  value       = module.journal_service.url
}

output "traditions_bucket_name" {
  description = "GCS bucket name for traditions"
  value       = module.base.traditions_bucket_name
}
