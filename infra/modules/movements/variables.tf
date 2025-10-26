variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "movements-service"
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