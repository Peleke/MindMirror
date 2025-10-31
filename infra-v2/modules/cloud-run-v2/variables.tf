# Cloud Run v2 Module Variables

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
}

variable "image" {
  description = "Container image URL"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for the Cloud Run service"
  type        = string
}

# ========================================
# SCALING
# ========================================

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

# ========================================
# SECRETS (Volume Mounts)
# ========================================

variable "secret_volumes" {
  description = "List of secrets to mount as volumes"
  type = list(object({
    volume_name = string # e.g., "database-url"
    secret_name = string # e.g., "DATABASE_URL"
    filename    = string # e.g., "database-url"
  }))
  default = []
}

# ========================================
# ENVIRONMENT VARIABLES (Non-Secret)
# ========================================

variable "env_vars" {
  description = "Environment variables (non-secret config only)"
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

# ========================================
# NETWORKING
# ========================================

variable "port" {
  description = "Container port"
  type        = number
  default     = 8000
}

variable "ingress" {
  description = "Ingress settings (INGRESS_TRAFFIC_ALL or INGRESS_TRAFFIC_INTERNAL_ONLY)"
  type        = string
  default     = "INGRESS_TRAFFIC_ALL"
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access (allUsers invoker role)"
  type        = bool
  default     = true
}

# ========================================
# HEALTH CHECKS
# ========================================

variable "health_check_path" {
  description = "Path for health check endpoint"
  type        = string
  default     = "/health"
}

variable "startup_probe_initial_delay" {
  description = "Startup probe initial delay in seconds"
  type        = number
  default     = 10
}

variable "startup_probe_timeout" {
  description = "Startup probe timeout in seconds"
  type        = number
  default     = 3
}

variable "startup_probe_period" {
  description = "Startup probe period in seconds"
  type        = number
  default     = 10
}

variable "startup_probe_failure_threshold" {
  description = "Startup probe failure threshold"
  type        = number
  default     = 3
}

# ========================================
# RESOURCES
# ========================================

variable "cpu_limit" {
  description = "CPU limit (e.g., 1000m = 1 vCPU)"
  type        = string
  default     = "1000m"
}

variable "memory_limit" {
  description = "Memory limit (e.g., 512Mi)"
  type        = string
  default     = "512Mi"
}
