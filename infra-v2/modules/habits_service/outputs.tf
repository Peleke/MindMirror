output "service_url" {
  description = "Habits service URL"
  value       = module.habits_service.service_url
}

output "service_name" {
  description = "Habits service name"
  value       = module.habits_service.service_name
}
