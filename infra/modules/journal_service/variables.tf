variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "journal-service"
}

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "journal_service_container_image" {
  description = "Journal service container image"
  type        = string
}

variable "service_account_email" {
  type = string
}

variable "gcs_bucket_name" {
  type = string
}



variable "faux_mesh_user_id" {
  type        = string
  description = "Fake user ID for mesh fallback"
}

variable "faux_mesh_supabase_id" {
  type        = string
  description = "Fake supabase ID for mesh fallback"
}

variable "log_level" {
  type        = string
  description = "Log level (e.g., INFO, DEBUG)"
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., development, production)"
}

variable "debug" {
  type        = string
  description = "Debug mode enabled (true/false)"
}

variable "database_url" {
  description = "PostgreSQL database URL"
  type        = string
}

variable "redis_url" {
  description = "Redis URL"
  type        = string
}

variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
}

variable "supabase_anon_key" {
  description = "Supabase anonymous key"
  type        = string
}

variable "supabase_service_role_key" {
  description = "Supabase service role key"
  type        = string
}

variable "supabase_ca_cert_path" {
  description = "Supabase CA certificate path"
  type        = string
}

variable "agent_service_url" {
  description = "Agent service URL"
  type        = string
}

variable "celery_worker_url" {
  description = "Celery worker URL"
  type        = string
}

variable "reindex_secret_key" {
  description = "Reindex secret key for celery worker authentication"
  type        = string
}

variable "users_service_url" {
  description = "Users service base URL"
  type        = string
}
