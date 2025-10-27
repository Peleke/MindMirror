# Gateway - Cloud Run v2
# GraphQL Hive Gateway federating all microservice schemas

module "gateway" {
  source = "../cloud-run-v2"

  project_id = var.project_id
  region     = var.region
  service_name = "gateway"
  image      = var.image

  # Gateway needs its own service account (created in base module via main.tf)
  service_account_email = "${var.project_id}@appspot.gserviceaccount.com" # Default compute SA for MVP

  # CRITICAL: User-facing, no cold starts
  min_instances = var.min_instances
  max_instances = var.max_instances

  # Secret volumes
  secret_volumes = [
    {
      volume_name = "supabase-anon-key"
      secret_name = var.supabase_anon_key_secret
      filename    = "supabase-anon-key"
    },
    {
      volume_name = "supabase-jwt-secret"
      secret_name = var.supabase_jwt_secret
      filename    = "supabase-jwt-secret"
    },
  ]

  # Environment variables
  env_vars = [
    {
      name  = "ENVIRONMENT"
      value = var.environment
    },
    {
      name  = "DEBUG"
      value = tostring(var.debug)
    },
    {
      name  = "PORT"
      value = "4000"
    },
    # Service URLs
    {
      name  = "AGENT_SERVICE_URL"
      value = var.agent_service_url
    },
    {
      name  = "JOURNAL_SERVICE_URL"
      value = var.journal_service_url
    },
    {
      name  = "HABITS_SERVICE_URL"
      value = var.habits_service_url
    },
    {
      name  = "MEALS_SERVICE_URL"
      value = var.meals_service_url
    },
    {
      name  = "MOVEMENTS_SERVICE_URL"
      value = var.movements_service_url
    },
    {
      name  = "PRACTICES_SERVICE_URL"
      value = var.practices_service_url
    },
    {
      name  = "USERS_SERVICE_URL"
      value = var.users_service_url
    },
    {
      name  = "VOUCHERS_WEB_BASE_URL"
      value = var.vouchers_web_base_url
    },
  ]

  # Networking
  port                  = 4000
  ingress               = "INGRESS_TRAFFIC_ALL" # Public gateway
  allow_unauthenticated = true

  # Health checks
  health_check_path                = "/healthcheck"
  startup_probe_initial_delay      = 15 # Gateway takes longer to start
  startup_probe_timeout            = 5
  startup_probe_period             = 15
  startup_probe_failure_threshold  = 5

  # Resources
  cpu_limit    = var.cpu_limit
  memory_limit = var.memory_limit
}
