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

# Service URLs
variable "users_service_url" {
  description = "Users service URL"
  type        = string
}

# Environment
variable "environment" {
  description = "Environment name"
  type        = string
}
