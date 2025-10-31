# Swae Production - Main Infrastructure

# ========================================
# BASE INFRASTRUCTURE
# ========================================

module "base" {
  source     = "./modules/base"
  project_id = var.project_id
  region     = var.region
}

# ========================================
# DATA SOURCES - SECRETS
# ========================================

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

data "google_secret_manager_secret_version" "reindex_secret_key" {
  secret  = "REINDEX_SECRET_KEY"
  project = var.project_id
}

# Service URLs (placeholder values on first deploy, updated after)
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

data "google_secret_manager_secret_version" "meals_service_url" {
  secret  = "MEALS_SERVICE_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "celery_worker_url" {
  secret  = "CELERY_WORKER_URL"
  project = var.project_id
}

data "google_secret_manager_secret_version" "vouchers_web_base_url" {
  secret  = "VOUCHERS_WEB_BASE_URL"
  project = var.project_id
}

# ========================================
# MICROSERVICES
# ========================================

# Users Service - CRITICAL (deploy first, no cold starts)
module "users_service" {
  source = "./modules/users_service"

  project_id            = var.project_id
  region                = var.region
  image                 = var.users_service_image
  service_account_email = module.base.users_service_sa_email

  # CRITICAL: Min instances = 1 (no cold starts)
  min_instances = var.min_instances_critical
  max_instances = var.max_instances

  # Secrets (volume mounts)
  database_url_secret = "DATABASE_URL"

  # Service URLs (from secrets - may be placeholders on first deploy)
  agent_service_url     = data.google_secret_manager_secret_version.agent_service_url.secret_data
  journal_service_url   = data.google_secret_manager_secret_version.journal_service_url.secret_data
  habits_service_url    = data.google_secret_manager_secret_version.habits_service_url.secret_data
  meals_service_url     = data.google_secret_manager_secret_version.meals_service_url.secret_data
  movements_service_url = module.movements_service.service_url
  practices_service_url = module.practices_service.service_url

  # Environment
  environment = var.environment
  log_level   = var.log_level
  debug       = var.debug
}

# Agent Service - CRITICAL (no cold starts)
module "agent_service" {
  source = "./modules/agent_service"

  project_id            = var.project_id
  region                = var.region
  image                 = var.agent_service_image
  service_account_email = module.base.agent_service_sa_email
  gcs_bucket_name       = module.base.traditions_bucket_name

  # CRITICAL: Min instances = 1
  min_instances = var.min_instances_critical
  max_instances = var.max_instances

  # Secrets (volume mounts)
  database_url_secret          = "DATABASE_URL"
  redis_url_secret             = "REDIS_URL"
  qdrant_url_secret            = "QDRANT_URL"
  qdrant_api_key_secret        = "QDRANT_API_KEY"
  openai_api_key_secret        = "OPENAI_API_KEY"
  supabase_url_secret          = "SUPABASE_URL"
  supabase_anon_key_secret     = "SUPABASE_ANON_KEY"
  supabase_service_role_secret = "SUPABASE_SERVICE_ROLE_KEY"

  # Service URLs
  celery_worker_url   = data.google_secret_manager_secret_version.celery_worker_url.secret_data
  journal_service_url = data.google_secret_manager_secret_version.journal_service_url.secret_data

  # Mesh config (legacy)
  faux_mesh_user_id     = var.faux_mesh_user_id
  faux_mesh_supabase_id = var.faux_mesh_supabase_id

  # Environment
  environment = var.environment
  log_level   = var.log_level
  debug       = var.debug
}

# Journal Service
module "journal_service" {
  source = "./modules/journal_service"

  project_id            = var.project_id
  region                = var.region
  image                 = var.journal_service_image
  service_account_email = module.base.journal_service_sa_email
  gcs_bucket_name       = module.base.traditions_bucket_name

  # Normal service (cold starts acceptable for MVP)
  min_instances = var.min_instances_normal
  max_instances = var.max_instances

  # Secrets
  database_url_secret          = "DATABASE_URL"
  redis_url_secret             = "REDIS_URL"
  supabase_url_secret          = "SUPABASE_URL"
  supabase_anon_key_secret     = "SUPABASE_ANON_KEY"
  supabase_service_role_secret = "SUPABASE_SERVICE_ROLE_KEY"
  reindex_secret_key_secret    = "REINDEX_SECRET_KEY"

  # Service URLs
  agent_service_url   = data.google_secret_manager_secret_version.agent_service_url.secret_data
  celery_worker_url   = data.google_secret_manager_secret_version.celery_worker_url.secret_data
  users_service_url   = module.users_service.service_url

  # Mesh config
  faux_mesh_user_id     = var.faux_mesh_user_id
  faux_mesh_supabase_id = var.faux_mesh_supabase_id

  # Environment
  environment = var.environment
  log_level   = var.log_level
  debug       = var.debug
}

# Habits Service
module "habits_service" {
  source = "./modules/habits_service"

  project_id            = var.project_id
  region                = var.region
  image                 = var.habits_service_image
  service_account_email = module.base.journal_service_sa_email

  min_instances = var.min_instances_normal
  max_instances = var.max_instances

  # Secrets
  database_url_secret = "DATABASE_URL"

  # Program template IDs
  uye_program_template_id              = var.uye_program_template_id
  mindmirror_program_template_id       = var.mindmirror_program_template_id
  daily_journaling_program_template_id = var.daily_journaling_program_template_id

  # Voucher web URL
  vouchers_web_base_url = data.google_secret_manager_secret_version.vouchers_web_base_url.secret_data

  # Environment
  environment = var.environment
  log_level   = var.log_level
}

# Meals Service
module "meals_service" {
  source = "./modules/meals_service"

  project_id            = var.project_id
  region                = var.region
  image                 = var.meals_service_image
  service_account_email = module.base.meals_service_sa_email

  min_instances = var.min_instances_normal
  max_instances = var.max_instances

  # Secrets
  database_url_secret = "DATABASE_URL"

  # Environment
  environment = var.environment
}

# Movements Service
module "movements_service" {
  source = "./modules/movements_service"

  project_id            = var.project_id
  region                = var.region
  image                 = var.movements_service_image
  service_account_email = module.base.movements_service_sa_email

  min_instances = var.min_instances_normal
  max_instances = var.max_instances

  # Secrets
  database_url_secret = "DATABASE_URL"

  # Environment
  environment = var.environment
}

# Practices Service
module "practices_service" {
  source = "./modules/practices_service"

  project_id            = var.project_id
  region                = var.region
  image                 = var.practices_service_image
  service_account_email = module.base.practices_service_sa_email

  min_instances = var.min_instances_normal
  max_instances = var.max_instances

  # Secrets
  database_url_secret = "DATABASE_URL"

  # Service URLs
  users_service_url = module.users_service.service_url

  # Environment
  environment = var.environment
}

# Gateway - CRITICAL (user-facing, no cold starts)
module "gateway" {
  source = "./modules/gateway"

  project_id = var.project_id
  region     = var.region
  image      = var.gateway_image

  # CRITICAL: Min instances = 1
  min_instances = var.min_instances_critical
  max_instances = var.max_instances

  # Secrets
  supabase_anon_key_secret = "SUPABASE_ANON_KEY"
  supabase_jwt_secret      = "SUPABASE_JWT_SECRET"

  # Service URLs
  agent_service_url     = data.google_secret_manager_secret_version.agent_service_url.secret_data
  journal_service_url   = data.google_secret_manager_secret_version.journal_service_url.secret_data
  habits_service_url    = data.google_secret_manager_secret_version.habits_service_url.secret_data
  meals_service_url     = data.google_secret_manager_secret_version.meals_service_url.secret_data
  movements_service_url = module.movements_service.service_url
  practices_service_url = module.practices_service.service_url
  users_service_url     = module.users_service.service_url
  vouchers_web_base_url = data.google_secret_manager_secret_version.vouchers_web_base_url.secret_data

  # Environment
  environment = var.environment
  debug       = var.debug
}

# Celery Worker (background tasks)
module "celery_worker" {
  source = "./modules/celery_worker"

  project_id = var.project_id
  region     = var.region
  image      = var.celery_worker_image

  # Background worker (normal scaling)
  min_instances = var.min_instances_normal
  max_instances = var.max_instances

  # Secrets
  database_url_secret       = "DATABASE_URL"
  redis_url_secret          = "REDIS_URL"
  qdrant_url_secret         = "QDRANT_URL"
  qdrant_api_key_secret     = "QDRANT_API_KEY"
  openai_api_key_secret     = "OPENAI_API_KEY"
  reindex_secret_key_secret = "REINDEX_SECRET_KEY"

  # Service URLs
  journal_service_url = data.google_secret_manager_secret_version.journal_service_url.secret_data
  agent_service_url   = data.google_secret_manager_secret_version.agent_service_url.secret_data

  # Environment
  environment = var.environment
  debug       = var.debug
}
