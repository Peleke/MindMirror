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

variable "reindex_secret_key_secret" {
  description = "Secret name for REINDEX_SECRET_KEY"
  type        = string
}

# Service URLs
variable "journal_service_url" {
  description = "Journal service URL"
  type        = string
}

variable "agent_service_url" {
  description = "Agent service URL"
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
