variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "gateway_container_image" {
  description = "Gateway container image"
  type        = string
}

variable "supabase_anon_key" {
  description = "Supabase anonymous key"
  type        = string
}

variable "supabase_jwt_secret" {
  description = "Supabase JWT secret"
  type        = string
}

variable "agent_service_url" {
  description = "Agent service URL"
  type        = string
}

variable "journal_service_url" {
  description = "Journal service URL"
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