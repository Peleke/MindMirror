# Agent Service - Cloud Run v2
# AI conversation engine with LangGraph orchestration, RAG via Qdrant

module "agent_service" {
  source = "../cloud-run-v2"

  project_id            = var.project_id
  region                = var.region
  service_name          = "agent-service"
  image                 = var.image
  service_account_email = var.service_account_email

  # CRITICAL: No cold starts for AI service
  min_instances = var.min_instances
  max_instances = var.max_instances

  # Secret volumes (mounted at /secrets/<volume-name>/<filename>)
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
      volume_name = "qdrant-url"
      secret_name = var.qdrant_url_secret
      filename    = "qdrant-url"
    },
    {
      volume_name = "qdrant-api-key"
      secret_name = var.qdrant_api_key_secret
      filename    = "qdrant-api-key"
    },
    {
      volume_name = "openai-api-key"
      secret_name = var.openai_api_key_secret
      filename    = "openai-api-key"
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
  ]

  # Environment variables (non-secret config)
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
      name  = "PROMPT_STORAGE_TYPE"
      value = "gcs"
    },
    {
      name  = "YAML_STORAGE_PATH"
      value = "/app/prompts"
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
    # LLM Configuration
    {
      name  = "LLM_PROVIDER"
      value = "openai"
    },
    {
      name  = "OPENAI_MODEL"
      value = "gpt-4o-mini"
    },
    {
      name  = "EMBEDDING_PROVIDER"
      value = "openai"
    },
    {
      name  = "EMBEDDING_MODEL"
      value = "text-embedding-3-small"
    },
    {
      name  = "EMBEDDING_VECTOR_SIZE"
      value = "1536"
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
      name  = "CELERY_WORKER_URL"
      value = var.celery_worker_url
    },
    {
      name  = "JOURNAL_SERVICE_URL"
      value = var.journal_service_url
    },
  ]

  # Networking
  port                  = 8000
  ingress               = "INGRESS_TRAFFIC_ALL" # MVP: Public
  allow_unauthenticated = true

  # Health checks
  health_check_path = "/health"

  # Resources
  cpu_limit    = var.cpu_limit
  memory_limit = var.memory_limit
}
