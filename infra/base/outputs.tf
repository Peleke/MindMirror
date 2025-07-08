output "journal_service_sa_email" {
  value = google_service_account.journal_service.email
}

output "agent_service_sa_email" {
  value = google_service_account.agent_service.email
}

output "traditions_bucket_name" {
  value = google_storage_bucket.traditions.name
}

output "secret_names" {
  value = {
    DATABASE_URL              = data.google_secret_manager_secret.database_url.name,
    REDIS_URL                = data.google_secret_manager_secret.redis_url.name,
    CELERY_BROKER_URL        = data.google_secret_manager_secret.celery_broker_url.name,
    AGENT_SERVICE_URL        = data.google_secret_manager_secret.agent_service_url.name,
    JWT_SECRET               = data.google_secret_manager_secret.jwt_secret.name,
    JWT_ALGORITHM            = data.google_secret_manager_secret.jwt_algorithm.name,
    SUPABASE_URL            = data.google_secret_manager_secret.supabase_url.name,
    SUPABASE_ANON_KEY       = data.google_secret_manager_secret.supabase_anon.name,
    SUPABASE_JWT_SECRET     = data.google_secret_manager_secret.supabase_jwt.name,
    SUPABASE_SERVICE_ROLE_KEY = data.google_secret_manager_secret.supabase_service_role_key.name,
    REINDEX_SECRET_KEY      = data.google_secret_manager_secret.reindex.name
  }
}