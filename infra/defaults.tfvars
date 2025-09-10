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
gateway_container_image         = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:9199557fe95470b72af32ceaf6c635e4646dea68"
# gateway_container_image         = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:d54d20b5f9db81c16bf6376c35ca3d945745c5a6"
celery_worker_container_image   = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/celery-worker:d6e5545f3b951048eeef06c98a00b2a6bf70d01f"
habits_service_container_image  = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/habits_service:3b3e40593f8990da0e099688740afbf4d108cef6"
meals_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/meals_service:20a8f95fa473cfc2d0f65f25d4c92bde03a26786"

users_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/users_service:74774db17dfe8d38a759261d0b22b2009f11118b"
movements_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/movements_service:2688e7b04019f7f997f4a774f0f178e82b4b39d8"
practices_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/practices_service:2688e7b04019f7f997f4a774f0f178e82b4b39d8"

# --- Mocking & Testing Fallbacks ---
# These are used for mesh compatibility and should be replaced with real values or logic if needed.
faux_mesh_supabase_id           = "00000000-0000-0000-0000-000000000002"
faux_mesh_user_id               = "00000000-0000-0000-0000-000000000001"

# Meals service
meals_env = {
  OFF_SEARCHALICIOUS_ENABLED = "true"
  OFF_USER_AGENT             = "MindMirrorMeals/1.0 (+support@mindmirror.app)"
}
