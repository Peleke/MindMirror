output "journal_service_url" {
  description = "Journal service Cloud Run URL"
  value       = module.journal_service.url
}

output "traditions_bucket_name" {
  description = "GCS bucket name for traditions"
  value       = module.base.traditions_bucket_name
}

output "agent_service_url" {
  description = "Agent service URL"
  value       = module.agent_service.agent_service_url
}

output "gateway_url" {
  description = "Gateway service URL"
  value       = module.gateway.gateway_url
}

# Deprecated: celery_worker module not in use
# output "celery_worker_url" {
#   description = "Celery worker service URL"
#   value       = module.celery_worker.celery_worker_url
# }

output "habits_service_url" {
  description = "Habits service URL"
  value       = module.habits_service.habits_service_url
}