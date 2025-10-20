variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "image" {
  description = "Container image"
  type        = string
}

variable "service_account_email" {
  description = "Service account email"
  type        = string
}

variable "gcs_bucket_name" {
  description = "GCS bucket for traditions/prompts"
  type        = string
}

variable "min_instances" {
  description = "Minimum instances"
  type        = number
}

variable "max_instances" {
  description = "Maximum instances"
  type        = number
}

# Secrets
variable "database_url_secret" {
  description = "Secret name for DATABASE_URL"
  type        = string
}

variable "redis_url_secret" {
  description = "Secret name for REDIS_URL"
  type        = string
}

variable "qdrant_url_secret" {
  description = "Secret name for QDRANT_URL"
  type        = string
}

variable "qdrant_api_key_secret" {
  description = "Secret name for QDRANT_API_KEY"
  type        = string
}

variable "openai_api_key_secret" {
  description = "Secret name for OPENAI_API_KEY"
  type        = string
}

variable "supabase_url_secret" {
  description = "Secret name for SUPABASE_URL"
  type        = string
}

variable "supabase_anon_key_secret" {
  description = "Secret name for SUPABASE_ANON_KEY"
  type        = string
}

variable "supabase_service_role_secret" {
  description = "Secret name for SUPABASE_SERVICE_ROLE_KEY"
  type        = string
}

# Service URLs
variable "celery_worker_url" {
  description = "Celery worker service URL"
  type        = string
}

variable "journal_service_url" {
  description = "Journal service URL"
  type        = string
}

# Mesh config (legacy)
variable "faux_mesh_user_id" {
  description = "Faux mesh user ID"
  type        = string
}

variable "faux_mesh_supabase_id" {
  description = "Faux mesh Supabase ID"
  type        = string
}

# Environment
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "log_level" {
  description = "Log level"
  type        = string
}

variable "debug" {
  description = "Debug mode"
  type        = bool
}

# Resources
variable "cpu_limit" {
  description = "CPU limit"
  type        = string
  default     = "1000m"
}

variable "memory_limit" {
  description = "Memory limit"
  type        = string
  default     = "512Mi"
}
