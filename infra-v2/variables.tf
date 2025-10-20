# Swae Production - OpenTofu Variables

# ========================================
# CORE CONFIGURATION
# ========================================

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (production, staging, etc.)"
  type        = string
  default     = "production"
}

# ========================================
# CONTAINER IMAGES
# ========================================

variable "agent_service_image" {
  description = "Docker image for agent service"
  type        = string
}

variable "journal_service_image" {
  description = "Docker image for journal service"
  type        = string
}

variable "habits_service_image" {
  description = "Docker image for habits service"
  type        = string
}

variable "meals_service_image" {
  description = "Docker image for meals service"
  type        = string
}

variable "movements_service_image" {
  description = "Docker image for movements service"
  type        = string
}

variable "practices_service_image" {
  description = "Docker image for practices service"
  type        = string
}

variable "users_service_image" {
  description = "Docker image for users service"
  type        = string
}

variable "gateway_image" {
  description = "Docker image for GraphQL gateway"
  type        = string
}

variable "celery_worker_image" {
  description = "Docker image for Celery worker"
  type        = string
}

# ========================================
# SCALING CONFIGURATION
# ========================================

variable "min_instances_critical" {
  description = "Minimum instances for critical services (users, gateway, agent)"
  type        = number
  default     = 1
}

variable "min_instances_normal" {
  description = "Minimum instances for normal services"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum instances per service"
  type        = number
  default     = 10
}

# ========================================
# RESOURCE LIMITS
# ========================================

variable "cpu_limit" {
  description = "CPU limit for services"
  type        = string
  default     = "1000m"
}

variable "memory_limit" {
  description = "Memory limit for services"
  type        = string
  default     = "512Mi"
}

# ========================================
# NETWORKING (for future VPC)
# ========================================

variable "enable_vpc_connector" {
  description = "Enable VPC connector for private mesh networking"
  type        = bool
  default     = false
}

variable "vpc_connector_cidr" {
  description = "CIDR range for VPC connector"
  type        = string
  default     = "10.8.0.0/28"
}

# ========================================
# PROGRAM TEMPLATE IDS (Habits Service)
# ========================================

variable "uye_program_template_id" {
  description = "UYE program template ID"
  type        = string
  default     = "uye-template"
}

variable "mindmirror_program_template_id" {
  description = "MindMirror program template ID"
  type        = string
  default     = "mindmirror-template"
}

variable "daily_journaling_program_template_id" {
  description = "Daily journaling program template ID"
  type        = string
  default     = "daily-journaling-template"
}

# ========================================
# DEBUG/LOGGING
# ========================================

variable "log_level" {
  description = "Log level for services"
  type        = string
  default     = "info"
}

variable "debug" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}

# ========================================
# MESH CONFIGURATION (Legacy - to be removed)
# ========================================

variable "faux_mesh_user_id" {
  description = "Faux mesh user ID for internal communication (legacy)"
  type        = string
  default     = "system"
}

variable "faux_mesh_supabase_id" {
  description = "Faux mesh Supabase ID for internal communication (legacy)"
  type        = string
  default     = "system"
}
