variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "agent-service"
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "agent_service_container_image" {
  description = "Agent service container image"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for GCS access"
  type        = string
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for storage"
  type        = string
}

variable "database_url" {
  description = "PostgreSQL database URL"
  type        = string
}

variable "redis_url" {
  description = "Redis URL"
  type        = string
}

variable "qdrant_url" {
  description = "Qdrant vector database URL"
  type        = string
}

variable "qdrant_api_key" {
  description = "Qdrant API key"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key"
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

variable "faux_mesh_user_id" {
  description = "Fake user ID for mesh fallback"
  type        = string
}

variable "faux_mesh_supabase_id" {
  description = "Fake supabase ID for mesh fallback"
  type        = string
}

variable "log_level" {
  description = "Log level (e.g., INFO, DEBUG)"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., development, production)"
  type        = string
}

variable "debug" {
  description = "Debug mode enabled (true/false)"
  type        = string
}

variable "celery_worker_url" {
  description = "Celery worker service URL"
  type        = string
}

variable "journal_service_url" {
  description = "Journal service URL"
  type        = string
} 
