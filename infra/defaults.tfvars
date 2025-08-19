# This file provides default variable values for a production-like environment.
# It is used by Terraform when no other .tfvars file is specified.

project_id                      = "mindmirror-69"
project_numerical_id            = "3858903851"
region                          = "us-east4"
gcs_bucket_name                 = "traditions-mindmirror-69"

# --- Logging and Environment ---
environment                     = "production"
log_level                       = "INFO"
debug                           = "false"

# --- Default Container Images ---
# These should point to the specific image tags you want to deploy.
# Using 'latest' is common for dev, but for production, specific commit SHAs are better.
journal_service_container_image = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/journal_service:d54d20b5f9db81c16bf6376c35ca3d945745c5a6"
agent_service_container_image   = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/agent_service:33f01f8be4e78ddc53a1befe438abeff8429ed63"
gateway_container_image         = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:f320f029e90510478c65473c31f933a1a8e6f6ae"
# gateway_container_image         = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:d54d20b5f9db81c16bf6376c35ca3d945745c5a6"
celery_worker_container_image   = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/celery-worker:d6e5545f3b951048eeef06c98a00b2a6bf70d01f"
habits_service_container_image  = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/habits_service:2cf96feba4e8925f4ba9a285b6d53eb274198826"

# --- Mocking & Testing Fallbacks ---
# These are used for mesh compatibility and should be replaced with real values or logic if needed.
faux_mesh_supabase_id           = "00000000-0000-0000-0000-000000000002"
faux_mesh_user_id               = "00000000-0000-0000-0000-000000000001" 
