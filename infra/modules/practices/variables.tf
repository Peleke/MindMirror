variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "practices-service"
}

variable "project_id" { type = string }

variable "region" { type = string }

variable "image" { type = string }

variable "service_account_email" { type = string }

variable "env" {
  type    = map(string)
  default = {}
}

variable "database_url" { type = string }

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  default     = "staging"
}

variable "enable_health_probes" {
  description = "Enable startup/liveness health probes"
  type        = bool
  default     = true
} 