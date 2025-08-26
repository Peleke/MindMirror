output "service_url" {
  value = google_cloud_run_service.practices.status[0].url
} 