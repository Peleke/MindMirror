output "service_url" {
  value = google_cloud_run_service.meals.status[0].url
} 