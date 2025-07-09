variable "project_id" {
  description = "GCP Project"
  type        = string
}

variable "project_numerical_id" {
  description = "GCP Project Numerical ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-east4"
}

variable "artifact_repo" {
  description = "Artifact registry"
  type = string
  default = "mindmirror"
}


variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "journal_service_container_image" {
  description = "Journal service container image"
  type        = string
}

variable "agent_service_container_image" {
  description = "Agent service container image"
  type        = string
  default     = "gcr.io/mindmirror-69/agent-service:latest"
}

variable "gateway_container_image" {
  description = "Gateway container image"
  type        = string
  default     = "gcr.io/mindmirror-69/gateway:latest"
}

variable "celery_worker_container_image" {
  description = "Celery worker container image"
  type        = string
  default     = "gcr.io/mindmirror-69/celery-worker:latest"
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for storage"
  type        = string
  # default     = "traditions"
}

variable "gcs_credential_file" {
  description = "Path to GCS credentials file"
  type        = string
}

variable "tradition_discovery_mode" {
  description = "Mode for tradition discovery"
  type        = string
  default     = "gcs-first"
}

variable "supabase_anon_key" {
  description = "Supabase anonymous key"
  type        = string
}

variable "supabase_service_role_key" {
  description = "Supabase service role key"
  type        = string
}

variable "supabase_jwt_secret" {
  description = "Supabase JWT secret"
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
  default     = "INFO"
}

variable "environment" {
  description = "Environment name (e.g., development, production)"
  type        = string
  default     = "production"
}

variable "debug" {
  description = "Debug mode enabled (true/false)"
  type        = string
  default     = "false"
}
