output "url" {
  value = google_cloud_run_service.journal_service.status[0].url
}

