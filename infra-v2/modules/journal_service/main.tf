# Journal Service - Cloud Run v2
# Manages structured journaling with automatic Qdrant indexing

module "journal_service" {
  source = "../cloud-run-v2"

  project_id            = var.project_id
  region                = var.region
  service_name          = "journal-service"
  image                 = var.image
  service_account_email = var.service_account_email

  # Normal service (cold starts acceptable for MVP)
  min_instances = var.min_instances
  max_instances = var.max_instances

  # Secret volumes
  secret_volumes = [
    {
      volume_name = "database-url"
      secret_name = var.database_url_secret
      filename    = "database-url"
    },
    {
      volume_name = "redis-url"
      secret_name = var.redis_url_secret
      filename    = "redis-url"
    },
    {
      volume_name = "supabase-url"
      secret_name = var.supabase_url_secret
      filename    = "supabase-url"
    },
    {
      volume_name = "supabase-anon-key"
      secret_name = var.supabase_anon_key_secret
      filename    = "supabase-anon-key"
    },
    {
      volume_name = "supabase-service-role-key"
      secret_name = var.supabase_service_role_secret
      filename    = "supabase-service-role-key"
    },
    {
      volume_name = "supabase-ca-cert-path"
      secret_name = "SUPABASE_CA_CERT_PATH"
      filename    = "supabase-ca-cert-path"
    },
    {
      volume_name = "reindex-secret-key"
      secret_name = var.reindex_secret_key_secret
      filename    = "reindex-secret-key"
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
      name  = "DEBUG"
      value = tostring(var.debug)
    },
    {
      name  = "PORT"
      value = "8000"
    },
    # GCS Configuration
    {
      name  = "GCS_BUCKET_NAME"
      value = var.gcs_bucket_name
    },
    {
      name  = "USE_GCS_EMULATOR"
      value = "false"
    },
    {
      name  = "STORAGE_EMULATOR_HOST"
      value = ""
    },
    {
      name  = "TRADITION_DISCOVERY_MODE"
      value = "gcs-only"
    },
    {
      name  = "GOOGLE_CLOUD_PROJECT"
      value = var.project_id
    },
    # Container flag
    {
      name  = "I_AM_IN_A_DOCKER_CONTAINER"
      value = "1"
    },
    # Mesh configuration (legacy)
    {
      name  = "FAUX_MESH_USER_ID"
      value = var.faux_mesh_user_id
    },
    {
      name  = "FAUX_MESH_SUPABASE_ID"
      value = var.faux_mesh_supabase_id
    },
    # Service URLs
    {
      name  = "AGENT_SERVICE_URL"
      value = var.agent_service_url
    },
    {
      name  = "CELERY_WORKER_URL"
      value = var.celery_worker_url
    },
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
  cpu_limit    = var.cpu_limit
  memory_limit = var.memory_limit
}
