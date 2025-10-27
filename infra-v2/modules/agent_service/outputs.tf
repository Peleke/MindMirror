output "service_url" {
  description = "Agent service URL"
  value       = module.agent_service.service_url
}

output "service_name" {
  description = "Agent service name"
  value       = module.agent_service.service_name
}
