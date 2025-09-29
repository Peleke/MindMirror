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
journal_service_container_image = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/journal_service:1403724fdd58e359e6256e765964a15b4990ad2b"
agent_service_container_image   = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/agent_service:33f01f8be4e78ddc53a1befe438abeff8429ed63"
gateway_container_image         = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:033479cc422bf71841f2876a00d02a6add9970f0"
celery_worker_container_image   = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/celery-worker:d6e5545f3b951048eeef06c98a00b2a6bf70d01f"
habits_service_container_image  = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/habits_service:82e2b8dbb7887c81d00fe007a8d03c4edb569340"
meals_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/meals_service:20a8f95fa473cfc2d0f65f25d4c92bde03a26786"

users_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/users_service:82e2b8dbb7887c81d00fe007a8d03c4edb569340"
movements_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/movements_service:c6c19c06ea43d505c31d7d9762db7f8f49544e4b"
practices_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/practices_service:243df244febdbbc2ccff45600a4538ec27deff06"

# --- Mocking & Testing Fallbacks ---
# These are used for mesh compatibility and should be replaced with real values or logic if needed.
faux_mesh_supabase_id           = "00000000-0000-0000-0000-000000000002"
faux_mesh_user_id               = "00000000-0000-0000-0000-000000000001"

# Meals service
meals_env = {
  OFF_SEARCHALICIOUS_ENABLED = "true"
  OFF_USER_AGENT             = "MindMirrorMeals/1.0 (+support@mindmirror.app)"
}
