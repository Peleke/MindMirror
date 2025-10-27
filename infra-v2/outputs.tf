# Swae Production - Outputs

# ========================================
# SERVICE URLS
# ========================================

output "gateway_url" {
  description = "GraphQL Gateway URL"
  value       = module.gateway.service_url
}

output "agent_service_url" {
  description = "Agent Service URL"
  value       = module.agent_service.service_url
}

output "journal_service_url" {
  description = "Journal Service URL"
  value        = module.journal_service.service_url
}

output "habits_service_url" {
  description = "Habits Service URL"
  value        = module.habits_service.service_url
}

output "meals_service_url" {
  description = "Meals Service URL"
  value        = module.meals_service.service_url
}

output "movements_service_url" {
  description = "Movements Service URL"
  value        = module.movements_service.service_url
}

output "practices_service_url" {
  description = "Practices Service URL"
  value        = module.practices_service.service_url
}

output "users_service_url" {
  description = "Users Service URL"
  value        = module.users_service.service_url
}

output "celery_worker_url" {
  description = "Celery Worker URL"
  value        = module.celery_worker.service_url
}

# ========================================
# INFRASTRUCTURE
# ========================================

output "traditions_bucket_name" {
  description = "GCS bucket for traditions/prompts"
  value       = module.base.traditions_bucket_name
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

# ========================================
# SERVICE ACCOUNT EMAILS
# ========================================

output "agent_service_sa_email" {
  description = "Agent Service service account email"
  value       = module.base.agent_service_sa_email
}

output "journal_service_sa_email" {
  description = "Journal Service service account email"
  value       = module.base.journal_service_sa_email
}

output "users_service_sa_email" {
  description = "Users Service service account email"
  value       = module.base.users_service_sa_email
}
