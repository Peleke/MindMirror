# Habits Service - Cloud Run v2
# Habit tracking and streaks

module "habits_service" {
  source = "../cloud-run-v2"

  project_id            = var.project_id
  region                = var.region
  service_name          = "habits-service"
  image                 = var.image
  service_account_email = var.service_account_email

  min_instances = var.min_instances
  max_instances = var.max_instances

  # Secret volumes
  secret_volumes = [
    {
      volume_name = "database-url"
      secret_name = var.database_url_secret
      filename    = "database-url"
    },
  ]

  # Environment variables
  env_vars = [
    {
      name  = "ENVIRONMENT"
      value = var.environment
    },
    {
      name  = "LOG_LEVEL"
      value = var.log_level
    },
    {
      name  = "PORT"
      value = "8003"
    },
    # Database pool settings
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
    # Program template IDs
    {
      name  = "UYE_PROGRAM_TEMPLATE_ID"
      value = var.uye_program_template_id
    },
    {
      name  = "MINDMIRROR_PROGRAM_TEMPLATE_ID"
      value = var.mindmirror_program_template_id
    },
    {
      name  = "DAILY_JOURNALING_PROGRAM_TEMPLATE_ID"
      value = var.daily_journaling_program_template_id
    },
    # Voucher web URL
    {
      name  = "VOUCHERS_WEB_BASE_URL"
      value = var.vouchers_web_base_url
    },
  ]

  # Networking
  port                  = 8003
  ingress               = "INGRESS_TRAFFIC_ALL"
  allow_unauthenticated = true

  # Health checks
  health_check_path = "/health"

  # Resources
  cpu_limit    = var.cpu_limit
  memory_limit = var.memory_limit
}
