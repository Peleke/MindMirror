variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "celery_worker_container_image" {
  description = "Celery worker container image"
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
  description = "Qdrant URL"
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

variable "reindex_secret_key" {
  description = "Reindex secret key"
  type        = string
}

variable "journal_service_url" {
  description = "Journal service URL"
  type        = string
}

variable "agent_service_url" {
  description = "Agent service URL"
  type        = string
}

variable "environment" {
  type        = string
  description = "Environment name (e.g., development, production)"
}

variable "debug" {
  type        = string
  description = "Debug mode enabled (true/false)"
} 