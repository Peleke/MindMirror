variable "project_id" { type = string }

variable "region" { type = string }

variable "service_name" { 
  type = string
  default = "meals-service"
}
variable "image" { type = string }

variable "service_account_email" { type = string }

variable "env" {
  type    = map(string)
  default = {}
}

variable "database_url" { type = string }
