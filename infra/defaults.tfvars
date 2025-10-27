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
journal_service_container_image = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/journal_service:7c6642b469d291bbe4d5f37f1848449f4b3d29d7"
agent_service_container_image   = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/agent_service:7c6642b469d291bbe4d5f37f1848449f4b3d29d7"
gateway_container_image         = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/mesh:033479cc422bf71841f2876a00d02a6add9970f0"
celery_worker_container_image   = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/celery-worker:d6e5545f3b951048eeef06c98a00b2a6bf70d01f"
habits_service_container_image  = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/habits_service:eed7bd9a9dfe13c2dc7350f32033b0d82d2677a5"
meals_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/meals_service:b95938c05f0a27d2ad30e84fecff63d670c3d2b8"

users_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/users_service:770a3eda0c455a057f050f06d49de44c2d191801"
movements_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/movements_service:e1503975f4368f4e2ce8303b884107534c8c379c"
practices_image        = "us-east4-docker.pkg.dev/mindmirror-69/mindmirror/practices_service:eed7bd9a9dfe13c2dc7350f32033b0d82d2677a5"

# --- Mocking & Testing Fallbacks ---
# These are used for mesh compatibility and should be replaced with real values or logic if needed.
faux_mesh_supabase_id           = "00000000-0000-0000-0000-000000000002"
faux_mesh_user_id               = "00000000-0000-0000-0000-000000000001"

# Meals service
meals_env = {
  OFF_SEARCHALICIOUS_ENABLED = "true"
  OFF_USER_AGENT             = "MindMirrorMeals/1.0 (+support@mindmirror.app)"
}
