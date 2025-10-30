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

output "meals_service_url" {
  description = "Meals service URL"
  value       = module.meals_service.service_url
}

output "movements_service_url" {
  description = "Movements service URL"
  value       = module.movements_service.service_url
}

output "practices_service_url" {
  description = "Practices service URL"
  value       = module.practices_service.service_url
}

output "users_service_url" {
  description = "Users service URL"
  value       = module.users_service.service_url
}