project_id        = "mindmirror-69"
region            = "us-east4"
artifact_repo     = "mindmirror"
image_tag         = "dev"
gcs_bucket_name   = "mindmirror-gcs-bucket"
gcs_credential_file = "/path/to/credentials.json"
tradition_discovery_mode = "gcs-first"

# Container images
journal_service_container_image = "gcr.io/mindmirror-69/journal-service:latest"
agent_service_container_image   = "gcr.io/mindmirror-69/agent-service:latest"
gateway_container_image         = "gcr.io/mindmirror-69/gateway:latest"
celery_worker_container_image   = "gcr.io/mindmirror-69/celery-worker:latest"

supabase_anon_key           = "YOUR_SUPABASE_ANON_KEY"
supabase_service_role_key   = "YOUR_SUPABASE_SERVICE_ROLE_KEY"
supabase_jwt_secret         = "YOUR_SUPABASE_JWT_SECRET"

agent_service_env_vars = {
  PROMPT_STORAGE_TYPE       = "gcs"
  YAML_STORAGE_PATH         = "/app/prompts"
  STORAGE_EMULATOR_HOST     = ""
  TRADITION_DISCOVERY_MODE  = "gcs-first"
  GCS_BUCKET_NAME           = "mindmirror-gcs-bucket"
  GCS_CREDENTIAL_FILE       = "/app/credentials.json"
  GCS_EMULATOR_HOST         = ""
  SUPABASE_ANON_KEY         = "YOUR_SUPABASE_ANON_KEY"
  SUPABASE_SERVICE_ROLE_KEY = "YOUR_SUPABASE_SERVICE_ROLE_KEY"
  SUPABASE_JWT_SECRET       = "YOUR_SUPABASE_JWT_SECRET"
}
