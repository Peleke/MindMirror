# Meals Service - Cloud Run v2
# Meal logging and nutrition tracking

module "meals_service" {
  source = "../cloud-run-v2"

  project_id            = var.project_id
  region                = var.region
  service_name          = "meals-service"
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
      name  = "MEALS_HTTP_PORT"
      value = "8000"
    },
    {
      name  = "PORT"
      value = "8000"
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
