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
