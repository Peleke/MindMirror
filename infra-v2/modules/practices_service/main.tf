# Practices Service - Cloud Run v2
# Meditation and mindfulness practices (workout programs)

module "practices_service" {
  source = "../cloud-run-v2"

  project_id            = var.project_id
  region                = var.region
  service_name          = "practices-service"
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
      name  = "PORT"
      value = "8000"
    },
    {
      name  = "API_VERSION"
      value = "0.1.0"
    },
    # Service URLs
    {
      name  = "USERS_SERVICE_URL"
      value = var.users_service_url
    },
  ]

  # Networking
  port                  = 8000
  ingress               = "INGRESS_TRAFFIC_ALL"
  allow_unauthenticated = true

  # Health checks
  health_check_path = "/health"

  # Resources
  cpu_limit    = "1000m"
  memory_limit = "512Mi"
}
