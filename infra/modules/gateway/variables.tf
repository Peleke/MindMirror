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

variable "habits_service_url" {
  description = "Habits service URL"
  type        = string
}

variable "meals_service_url" {
  description = "Meals service URL"
  type        = string
}

variable "vouchers_web_base_url" {
  description = "Base URL of the web app exposing vouchers REST endpoints"
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