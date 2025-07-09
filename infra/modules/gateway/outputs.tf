output "gateway_url" {
  description = "Gateway service URL"
  value       = google_cloud_run_service.gateway.status[0].url
}

output "gateway_service_account_email" {
  description = "Gateway service account email"
  value       = google_service_account.gateway.email
} 