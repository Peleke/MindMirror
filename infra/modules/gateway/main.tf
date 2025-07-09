resource "google_cloud_run_service" "gateway" {
  name     = "gateway"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = var.gateway_container_image

        ports {
          container_port = 4000
        }

        # Supabase Configuration
        env {
          name  = "SUPABASE_ANON_KEY"
          value = var.supabase_anon_key
        }

        env {
          name  = "SUPABASE_JWT_SECRET"
          value = var.supabase_jwt_secret
        }

        # Service URLs for subgraphs
        env {
          name  = "AGENT_SERVICE_URL"
          value = var.agent_service_url
        }

        env {
          name  = "JOURNAL_SERVICE_URL"
          value = var.journal_service_url
        }

        # Environment
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DEBUG"
          value = var.debug
        }
      }

      service_account_name = google_service_account.gateway.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.gateway.location
  project  = google_cloud_run_service.gateway.project
  service  = google_cloud_run_service.gateway.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Service account for gateway
resource "google_service_account" "gateway" {
  account_id   = "gateway"
  display_name = "Service Account for Gateway"
  project      = var.project_id
}

# Secret Manager access for gateway
resource "google_project_iam_member" "gateway_sa_secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.gateway.email}"
} 