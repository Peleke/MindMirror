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

variable "min_instances" {
  description = "Minimum instances"
  type        = number
}

variable "max_instances" {
  description = "Maximum instances"
  type        = number
}

# Secrets
variable "supabase_anon_key_secret" {
  description = "Secret name for SUPABASE_ANON_KEY"
  type        = string
}

variable "supabase_jwt_secret" {
  description = "Secret name for SUPABASE_JWT_SECRET"
  type        = string
}

# Service URLs
variable "agent_service_url" {
  description = "Agent service URL"
  type        = string
}

variable "journal_service_url" {
  description = "Journal service URL"
  type        = string
}

variable "habits_service_url" {
  description = "Habits service URL"
  type        = string
}

variable "meals_service_url" {
  description = "Meals service URL"
  type        = string
}

variable "movements_service_url" {
  description = "Movements service URL"
  type        = string
}

variable "practices_service_url" {
  description = "Practices service URL"
  type        = string
}

variable "users_service_url" {
  description = "Users service URL"
  type        = string
}

variable "vouchers_web_base_url" {
  description = "Vouchers web base URL"
  type        = string
}

# Environment
variable "environment" {
  description = "Environment name"
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
