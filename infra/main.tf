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

data "google_secret_manager_secret_version" "supabase_jwt_secret" {
  secret  = "SUPABASE_JWT_SECRET"
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

data "google_secret_manager_secret_version" "qdrant_url" {
  secret  = "QDRANT_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "qdrant_api_key" {
  secret  = "QDRANT_API_KEY"
  project = var.project_id
}

data "google_secret_manager_secret_version" "openai_api_key" {
  secret  = "OPENAI_API_KEY"
  project = var.project_id
}

data "google_secret_manager_secret_version" "agent_service_url" {
  secret  = "AGENT_SERVICE_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "journal_service_url" {
  secret  = "JOURNAL_SERVICE_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "habits_service_url" {
  secret  = "HABITS_SERVICE_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "vouchers_web_base_url" {
  secret  = "VOUCHERS_WEB_BASE_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "celery_worker_url" {
  secret  = "CELERY_WORKER_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "reindex_secret_key" {
  secret  = "REINDEX_SECRET_KEY"
  project = var.project_id
}

data "google_secret_manager_secret_version" "meals_service_url" {
  secret  = "MEALS_SERVICE_URL"
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
  
  # Service URLs (from secrets)
  agent_service_url     = data.google_secret_manager_secret_version.agent_service_url.secret_data
  celery_worker_url     = data.google_secret_manager_secret_version.celery_worker_url.secret_data
  
  # Security (from secrets)
  reindex_secret_key    = data.google_secret_manager_secret_version.reindex_secret_key.secret_data
}

module "agent_service" {
  source  = "./modules/agent_service"
  
  project_id  = var.project_id
  region      = var.region
  agent_service_container_image = var.agent_service_container_image
  service_account_email = module.base.agent_service_sa_email
  gcs_bucket_name = module.base.traditions_bucket_name
  
  # Database and Redis (from secrets)
  database_url          = data.google_secret_manager_secret_version.database_url.secret_data
  redis_url             = data.google_secret_manager_secret_version.redis_url.secret_data
  
  # Vector database (from secrets)
  qdrant_url            = data.google_secret_manager_secret_version.qdrant_url.secret_data
  qdrant_api_key        = data.google_secret_manager_secret_version.qdrant_api_key.secret_data
  
  # LLM configuration (from secrets)
  openai_api_key        = data.google_secret_manager_secret_version.openai_api_key.secret_data
  
  # Supabase configuration (from secrets)
  supabase_url          = data.google_secret_manager_secret_version.supabase_url.secret_data
  supabase_anon_key     = data.google_secret_manager_secret_version.supabase_anon_key.secret_data
  supabase_service_role_key = data.google_secret_manager_secret_version.supabase_service_role_key.secret_data
  
  # Mesh configuration
  faux_mesh_user_id     = var.faux_mesh_user_id
  faux_mesh_supabase_id = var.faux_mesh_supabase_id
  
  # Service URLs (from secrets)
  celery_worker_url     = data.google_secret_manager_secret_version.celery_worker_url.secret_data
  journal_service_url   = data.google_secret_manager_secret_version.journal_service_url.secret_data
  
  # Logging and environment
  log_level             = var.log_level
  environment           = var.environment
  debug                 = var.debug
}

module "gateway" {
  source  = "./modules/gateway"
  
  project_id  = var.project_id
  region      = var.region
  gateway_container_image = var.gateway_container_image
  
  # Supabase configuration (from secrets)
  supabase_anon_key     = data.google_secret_manager_secret_version.supabase_anon_key.secret_data
  supabase_jwt_secret   = data.google_secret_manager_secret_version.supabase_jwt_secret.secret_data
  
  # Service URLs (from secrets)
  agent_service_url     = data.google_secret_manager_secret_version.agent_service_url.secret_data
  journal_service_url   = data.google_secret_manager_secret_version.journal_service_url.secret_data
  habits_service_url    = data.google_secret_manager_secret_version.habits_service_url.secret_data
  meals_service_url     = data.google_secret_manager_secret_version.meals_service_url.secret_data
  vouchers_web_base_url = data.google_secret_manager_secret_version.vouchers_web_base_url.secret_data
  
  # Environment
  environment           = var.environment
  debug                 = var.debug
}

module "celery_worker" {
  source  = "./modules/celery-worker"
  
  project_id  = var.project_id
  project_numerical_id = var.project_numerical_id
  region      = var.region
  celery_worker_container_image = var.celery_worker_container_image
  
  # Database and Redis (from secrets)
  database_url          = data.google_secret_manager_secret_version.database_url.secret_data
  redis_url             = data.google_secret_manager_secret_version.redis_url.secret_data
  
  # Vector database (from secrets)
  qdrant_url            = data.google_secret_manager_secret_version.qdrant_url.secret_data
  qdrant_api_key        = data.google_secret_manager_secret_version.qdrant_api_key.secret_data
  
  # LLM configuration (from secrets)
  openai_api_key        = data.google_secret_manager_secret_version.openai_api_key.secret_data
  
  # Security (from secrets)
  reindex_secret_key    = data.google_secret_manager_secret_version.reindex_secret_key.secret_data
  
  # Service URLs (from secrets)
  journal_service_url   = data.google_secret_manager_secret_version.journal_service_url.secret_data
  agent_service_url     = data.google_secret_manager_secret_version.agent_service_url.secret_data
  
  # Environment
  environment           = var.environment
  debug                 = var.debug
}

module "habits_service" {
  source  = "./modules/habits_service"

  project_id  = var.project_id
  region      = var.region
  habits_service_container_image = var.habits_service_container_image
  service_account_email = module.base.journal_service_sa_email

  # Logging and environment
  log_level   = var.log_level
  environment = var.environment

  database_url                 = data.google_secret_manager_secret_version.database_url.secret_data
  vouchers_web_base_url        = data.google_secret_manager_secret_version.vouchers_web_base_url.secret_data
  uye_program_template_id      = var.uye_program_template_id
  mindmirror_program_template_id = var.mindmirror_program_template_id
  daily_journaling_program_template_id = var.daily_journaling_program_template_id
}

module "meals_service" {
  source       = "./modules/meals"
  project_id   = var.project_id
  region       = var.region
  service_name = "meals-service"
  image        = var.meals_image
  env          = var.meals_env
  database_url = data.google_secret_manager_secret_version.database_url.secret_data
  service_account_email = module.base.meals_service_email
}

output "meals_service_url" {
  value = module.meals_service.service_url
}