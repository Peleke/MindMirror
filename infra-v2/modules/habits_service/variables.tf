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

# Program template IDs
variable "uye_program_template_id" {
  description = "UYE program template ID"
  type        = string
}

variable "mindmirror_program_template_id" {
  description = "MindMirror program template ID"
  type        = string
}

variable "daily_journaling_program_template_id" {
  description = "Daily journaling program template ID"
  type        = string
}

# Voucher web URL
variable "vouchers_web_base_url" {
  description = "Vouchers web base URL"
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
