output "habits_service_url" {
  description = "Habits service Cloud Run URL"
  value       = google_cloud_run_service.habits_service.status[0].url
}
