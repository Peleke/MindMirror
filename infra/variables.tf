variable "project_id" {
  description = "GCP Project"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-east4"
}

variable "artifact_repo" {
  description = "Artifact registry"
  type = string
  default = "mindmirror"
}


variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for storage"
  type        = string
  # default     = "traditions"
}

variable "gcs_credential_file" {
  description = "Path to GCS credentials file"
  type        = string
}

variable "tradition_discovery_mode" {
  description = "Mode for tradition discovery"
  type        = string
  default     = "gcs-first"
}

variable "supabase_anon_key" {
  description = "Supabase anonymous key"
  type        = string
}

variable "supabase_service_role_key" {
  description = "Supabase service role key"
  type        = string
}

variable "supabase_jwt_secret" {
  description = "Supabase JWT secret"
  type        = string
}
