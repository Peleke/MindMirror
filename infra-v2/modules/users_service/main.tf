# Users Service - Cloud Run v2
# CRITICAL SERVICE: Min instances = 1 (no cold starts)
# Entire system depends on this service for user lookups

module "users_service" {
  source = "../cloud-run-v2"

  project_id            = var.project_id
  region                = var.region
  service_name          = "users-service"
  image                 = var.image
  service_account_email = var.service_account_email

  # CRITICAL: No cold starts
  min_instances = var.min_instances
  max_instances = var.max_instances

  # Secret volumes (mounted at /secrets/<volume-name>/<filename>)
  secret_volumes = [
    {
      volume_name = "database-url"
      secret_name = var.database_url_secret
      filename    = "database-url"
    },
  ]

  # Environment variables (non-secret config)
  env_vars = concat([
    {
      name  = "ENVIRONMENT"
      value = var.environment
    },
    {
      name  = "LOG_LEVEL"
      value = var.log_level
    },
    {
      name  = "DEBUG"
      value = tostring(var.debug)
    },
    {
      name  = "PORT"
      value = "8000"
    },
    # Database connection pooling
    {
      name  = "DB_POOL_SIZE"
      value = "10"
    },
    {
      name  = "DB_MAX_OVERFLOW"
      value = "20"
    },
    {
      name  = "DB_POOL_TIMEOUT"
      value = "10"
    },
    {
      name  = "DB_POOL_RECYCLE"
      value = "1800"
    },
    {
      name  = "DB_POOL_PRE_PING"
      value = "true"
    },
  ],
  # Service URLs (for inter-service communication)
  [
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
  ])

  # Networking
  port                    = 8000
  ingress                 = "INGRESS_TRAFFIC_ALL" # MVP: Public (will change to INTERNAL_ONLY after VPC)
  allow_unauthenticated   = true

  # Health checks
  health_check_path = "/health"

  # Resources
  cpu_limit    = "1000m"
  memory_limit = "512Mi"
}
