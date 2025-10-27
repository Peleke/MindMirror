output "service_url" {
  description = "Users service URL"
  value       = module.users_service.service_url
}

output "service_name" {
  description = "Users service name"
  value       = module.users_service.service_name
}
