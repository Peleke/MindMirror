module "base" {
  source     = "./base"
  project_id = var.project_id
  region     = var.region
}

# Data sources for secrets
data "google_secret_manager_secret_version" "database_url" {
  secret  = "DATABASE_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "redis_url" {
  secret  = "REDIS_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "supabase_url" {
  secret  = "SUPABASE_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "supabase_anon_key" {
  secret  = "SUPABASE_ANON_KEY"
  project = var.project_id
}

data "google_secret_manager_secret_version" "supabase_service_role_key" {
  secret  = "SUPABASE_SERVICE_ROLE_KEY"
  project = var.project_id
}

data "google_secret_manager_secret_version" "supabase_ca_cert_path" {
  secret  = "SUPABASE_CA_CERT_PATH"
  project = var.project_id
}

module "journal_service" {
  source                = "./modules/journal_service"
  project_id            = var.project_id
  region                = var.region
  journal_service_container_image = var.journal_service_container_image
  service_account_email = module.base.journal_service_sa_email
  gcs_bucket_name       = module.base.traditions_bucket_name
  
  # Database and Redis (from secrets)
  database_url          = data.google_secret_manager_secret_version.database_url.secret_data
  redis_url             = data.google_secret_manager_secret_version.redis_url.secret_data
  
  # Supabase configuration (from secrets)
  supabase_url          = data.google_secret_manager_secret_version.supabase_url.secret_data
  supabase_anon_key     = data.google_secret_manager_secret_version.supabase_anon_key.secret_data
  supabase_service_role_key = data.google_secret_manager_secret_version.supabase_service_role_key.secret_data
  supabase_ca_cert_path = data.google_secret_manager_secret_version.supabase_ca_cert_path.secret_data
  
  # Mesh configuration
  faux_mesh_user_id     = var.faux_mesh_user_id
  faux_mesh_supabase_id = var.faux_mesh_supabase_id
  
  # Logging and environment
  log_level             = var.log_level
  environment           = var.environment
  debug                 = var.debug
}

# module "agent_service" {
#   source  = "./modules/agent_service"
# 
#   project_id  = var.project_id
#   region      = var.region
#   container_image = var.agent_service_container_image
#   agent_service_env_vars = {
#     PROMPT_STORAGE_TYPE    = "gcs"
#     YAML_STORAGE_PATH      = "/app/prompts"
#     STORAGE_EMULATOR_HOST  = "" # leave blank for prod
#     TRADITION_DISCOVERY_MODE = "gcs-first"
#     GCS_BUCKET_NAME = var.gcs_bucket_name
#     GCS_CREDENTIAL_FILE = var.gcs_credential_file
#     GCS_EMULATOR_HOST=""
#     TRADITION_DISCOVERY_MODE = var.tradition_discovery_mode
#     SUPABASE_ANON_KEY = var.supabase_anon_key
#     SUPABASE_SERVICE_ROLE_KEY = var.supabase_service_role_key
#     SUPABASE_JWT_SECRET = var.supabase_jwt_secret
#   }
# }
# 
# 