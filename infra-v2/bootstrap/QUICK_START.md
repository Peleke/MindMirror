# Quick Start: Production Bootstrap

## Prerequisites
- `gcloud` CLI installed and authenticated
- Production GCP project `mindmirror-prod` exists
- GitHub repository access

## Run This Command

```bash
cd infra-v2/bootstrap
./bootstrap-production.sh
```

That's it! The orchestrator will:
1. ✅ Create Artifact Registry for Docker images
2. ✅ Create GCS bucket for Terraform state
3. ✅ Create service account for GitHub Actions
4. ✅ Set up Workload Identity Federation

## After Bootstrap

Add this GitHub repository secret:

```bash
# Get project number
gcloud projects describe mindmirror-prod --format='value(projectNumber)'

# Add to GitHub:
# Name: GCP_PRODUCTION_PROJECT_NUM
# Value: [output from above command]
```

## Test Deployment

```bash
# Trigger workflow
git push origin main

# Monitor
gh run list --workflow production-deploy.yml --limit 1
gh run watch
```

## What Gets Created

| Resource | Name | Location |
|----------|------|----------|
| State Bucket | `mindmirror-tofu-state` | us-east4 |
| Artifact Registry | `mindmirror` | us-east4 |
| Service Account | `github-actions-production@mindmirror-prod.iam.gserviceaccount.com` | Global |
| WIF Pool | `github-pool` | Global |
| WIF Provider | `github-oidc` | Global |

## For Staging

Same process, different command:

```bash
./bootstrap-staging.sh
```

Creates everything in `mindmirror-69` project with `-staging` suffixes.
