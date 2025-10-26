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

# Service names (allows parallel stack deployment with -auto suffix)
variable "agent_service_name" {
  description = "Agent service Cloud Run name"
  type        = string
  default     = "agent-service"
}

variable "journal_service_name" {
  description = "Journal service Cloud Run name"
  type        = string
  default     = "journal-service"
}

variable "habits_service_name" {
  description = "Habits service Cloud Run name"
  type        = string
  default     = "habits-service"
}

variable "gateway_service_name" {
  description = "Gateway service Cloud Run name"
  type        = string
  default     = "gateway"
}

variable "meals_service_name" {
  description = "Meals service Cloud Run name"
  type        = string
  default     = "meals-service"
}

variable "movements_service_name" {
  description = "Movements service Cloud Run name"
  type        = string
  default     = "movements-service"
}

variable "practices_service_name" {
  description = "Practices service Cloud Run name"
  type        = string
  default     = "practices-service"
}

variable "users_service_name" {
  description = "Users service Cloud Run name"
  type        = string
  default     = "users-service"
}

variable "celery_worker_service_name" {
  description = "Celery worker service Cloud Run name"
  type        = string
  default     = "celery-worker-web"
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

variable "habits_service_container_image" {
  description = "Habits service container image"
  type        = string
  default     = "gcr.io/mindmirror-69/habits-service:latest"
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

variable "tradition_discovery_mode" {
  description = "Mode for tradition discovery"
  type        = string
  default     = "gcs-first"
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

variable "vouchers_web_base_url" {
  description = "Base URL of web app exposing vouchers REST"
  type        = string
  default     = "https://mind-mirror-seven.vercel.app"
}

variable "uye_program_template_id" {
  description = "Program template ID for UYE"
  type        = string
  default     = "be925a11-edfa-4208-9924-d0ecae956aac"
}

variable "mindmirror_program_template_id" {
  description = "Program template ID for MindMirror"
  type        = string
  default     = "1b4fa08a-462b-445e-85a6-6da4d70c6ed"
}

variable "daily_journaling_program_template_id" {
  description = "Program template ID for Daily Journaling"
  type        = string
  default     = "1b4fa08a-462b-445e-85a6-6da4d70c6ed"
}

# Meals vars
variable "meals_image" { type = string }
variable "meals_env" { type = map(string) }

# New service images
variable "users_image" { type = string }
variable "movements_image" { type = string }
variable "practices_image" { type = string }
