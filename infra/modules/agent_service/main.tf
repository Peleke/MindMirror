resource "google_cloud_run_service" "default" {
  name     = "agent-service"
  location = var.region

  template {
    spec {
      containers {
        image = var.container_image

        dynamic "env" {
          for_each = var.agent_service_env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        ports {
          container_port = 8000
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

output "agent_service_url" {
  value = google_cloud_run_service.default.status[0].url
}

