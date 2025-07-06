variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "container_image" {
  description = "Container image URL"
  type        = string
}

variable "agent_service_env_vars" {
  description = "Environment variables for the agent service"
  type        = map(string)
} 
