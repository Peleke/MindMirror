module "agent_service" {
  source  = "./modules/agent_service"

  project_id  = var.project_id
  region      = var.region
  container_image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo}/agent_service:${var.image_tag}"
  agent_service_env_vars = {
    PROMPT_STORAGE_TYPE    = "gcs"
    YAML_STORAGE_PATH      = "/app/prompts"
    STORAGE_EMULATOR_HOST  = "" # leave blank for prod
    TRADITION_DISCOVERY_MODE = "gcs-first"
    GCS_BUCKET_NAME = var.gcs_bucket_name
    GCS_CREDENTIAL_FILE = var.gcs_credential_file
    GCS_EMULATOR_HOST=""
    TRADITION_DISCOVERY_MODE = var.tradition_discovery_mode
    SUPABASE_ANON_KEY = var.supabase_anon_key
    SUPABASE_SERVICE_ROLE_KEY = var.supabase_service_role_key
    SUPABASE_JWT_SECRET = var.supabase_jwt_secret
  }
}

