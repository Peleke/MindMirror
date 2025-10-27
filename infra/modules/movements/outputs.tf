output "service_url" {
  value = google_cloud_run_service.movements.status[0].url
} 