provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "traditions" {
  name     = "traditions-${var.project_id}"
  location = var.region
  project  = var.project_id

  uniform_bucket_level_access = true
  force_destroy               = false
}

resource "google_service_account" "journal_service" {
  account_id   = "journal-service"
  display_name = "Service Account for Journal Service"
  project      = var.project_id
}

resource "google_storage_bucket_iam_member" "journal_sa_gcs_access" {
  bucket = google_storage_bucket.traditions.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.journal_service.email}"
}

resource "google_project_iam_member" "journal_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.journal_service.email}"
}

resource "google_service_account" "agent_service" {
  account_id   = "agent-service"
  display_name = "Service Account for Agent Service"
  project      = var.project_id
}

resource "google_storage_bucket_iam_member" "agent_sa_gcs_access" {
  bucket = google_storage_bucket.traditions.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_storage_bucket_iam_member" "agent_sa_bucket_access" {
  bucket = google_storage_bucket.traditions.name
  role   = "roles/storage.legacyBucketReader"
  member = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_project_iam_member" "agent_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.agent_service.email}"
}

resource "google_service_account" "meals_service" {
  account_id   = "meals-service"
  display_name = "Service Account for Meals Service"
  project      = var.project_id
}

resource "google_project_iam_member" "meals_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.meals_service.email}"
}

output "meals_service_email" {
  value = google_service_account.meals_service.email
}

# Existing secrets — just referencing
data "google_secret_manager_secret" "reindex" {
  secret_id = "REINDEX_SECRET_KEY"
  project   = var.project_id
}

data "google_secret_manager_secret" "supabase_anon" {
  secret_id = "SUPABASE_ANON_KEY" 
  project   = var.project_id
}

data "google_secret_manager_secret" "supabase_jwt" {
  secret_id = "SUPABASE_JWT_SECRET"
  project   = var.project_id
}

data "google_secret_manager_secret" "database_url" {
  secret_id = "DATABASE_URL"
  project   = var.project_id
}

data "google_secret_manager_secret" "redis_url" {
  secret_id = "REDIS_URL"
  project   = var.project_id
}

data "google_secret_manager_secret" "celery_broker_url" {
  secret_id = "CELERY_BROKER_URL"
  project   = var.project_id
}

data "google_secret_manager_secret" "agent_service_url" {
  secret_id = "AGENT_SERVICE_URL"
  project   = var.project_id
}

data "google_secret_manager_secret" "jwt_secret" {
  secret_id = "JWT_SECRET"
  project   = var.project_id
}

data "google_secret_manager_secret" "jwt_algorithm" {
  secret_id = "JWT_ALGORITHM"
  project   = var.project_id
}

data "google_secret_manager_secret" "supabase_url" {
  secret_id = "SUPABASE_URL"
  project   = var.project_id
}

data "google_secret_manager_secret" "supabase_service_role_key" {
  secret_id = "SUPABASE_SERVICE_ROLE_KEY"
  project   = var.project_id
}
