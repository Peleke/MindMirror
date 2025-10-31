variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "habits-service"
}

variable "project_id" { type = string }
variable "region" { type = string }
variable "habits_service_container_image" { type = string }
variable "service_account_email" { type = string }
variable "environment" { type = string }
variable "log_level" { type = string }

variable "database_url" { type = string }

variable "vouchers_web_base_url" { type = string }
variable "uye_program_template_id" { type = string }
variable "mindmirror_program_template_id" { type = string }

variable "daily_journaling_program_template_id" { type = string }
