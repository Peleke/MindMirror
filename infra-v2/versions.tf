terraform {
  required_version = ">= 1.8.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  # Remote state in GCS
  # Initialize with: tofu init -backend-config="bucket=swae-tofu-state"
  backend "gcs" {
    prefix = "production/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
