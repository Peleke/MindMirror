# Swae Base Infrastructure

# GCS Bucket for traditions/prompts storage
resource "google_storage_bucket" "traditions" {
  name     = "traditions-${var.project_id}"
  location = var.region
  project  = var.project_id

  uniform_bucket_level_access = true
  force_destroy               = false

  versioning {
    enabled = true
  }
}

# ========================================
# SERVICE ACCOUNTS
# ========================================

# Agent Service
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

resource "google_project_iam_member" "agent_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.agent_service.email}"
}

# Journal Service
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

# Meals Service
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

# Movements Service
resource "google_service_account" "movements_service" {
  account_id   = "movements-service"
  display_name = "Service Account for Movements Service"
  project      = var.project_id
}

resource "google_project_iam_member" "movements_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.movements_service.email}"
}

# Practices Service
resource "google_service_account" "practices_service" {
  account_id   = "practices-service"
  display_name = "Service Account for Practices Service"
  project      = var.project_id
}

resource "google_project_iam_member" "practices_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.practices_service.email}"
}

# Users Service
resource "google_service_account" "users_service" {
  account_id   = "users-service"
  display_name = "Service Account for Users Service"
  project      = var.project_id
}

resource "google_project_iam_member" "users_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.users_service.email}"
}
