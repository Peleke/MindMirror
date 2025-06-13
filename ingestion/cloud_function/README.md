# Cloud Function for GCS-Triggered Re-indexing

This directory contains the code for a Google Cloud Function that automatically triggers the re-indexing of a "tradition" when a new document is uploaded to its corresponding folder in a GCS bucket.

## Functionality

- **Trigger:** Fires when a file is created or updated in a GCS bucket (`google.storage.object.finalize`).
- **Action:**
    1. Parses the file path to determine the `tradition` (e.g., `canon-default` from `canon-default/documents/my-file.pdf`).
    2. Makes a secure `POST` request to the application's `/triggers/reindex-tradition` webhook.
    3. Passes the `tradition` as a query parameter and includes a secret key in the `X-Reindex-Secret` header for authentication.

## Deployment

This function is designed to be deployed using the `gcloud` command-line tool.

### Prerequisites

1.  Google Cloud SDK (`gcloud`) is installed and authenticated.
2.  You have a GCS bucket for your traditions.
3.  Your FastAPI application is deployed and accessible via a public URL.

### Deployment Command

Navigate to the root of the repository and run the following command. **Remember to replace the placeholder values.**

```bash
# Set your variables
export PROJECT_ID="your-gcp-project-id"
export REGION="your-preferred-region" # e.g., us-central1
export GCS_BUCKET="your-traditions-bucket-name"
export API_URL="https://your-fastapi-app-url.com/triggers/reindex-tradition"
export SECRET_KEY="your-super-secret-reindex-key"

# Deploy the function
gcloud functions deploy trigger-reindex-tradition \
  --gen2 \
  --project=${PROJECT_ID} \
  --region=${REGION} \
  --runtime=python311 \
  --source=./ingestion/cloud_function \
  --entry-point=trigger_reindex_on_gcs_upload \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=${GCS_BUCKET}" \
  --set-env-vars API_WEBHOOK_URL=${API_URL},REINDEX_SECRET_KEY=${SECRET_KEY}
```

### Environment Variables

The function requires the following environment variables to be set during deployment:

-   `API_WEBHOOK_URL`: The full URL to the `/triggers/reindex-tradition` endpoint on your running application.
-   `REINDEX_SECRET_KEY`: The secret key that the application uses to authenticate requests to the trigger endpoint. This must match the `REINDEX_SECRET_KEY` set in your application's environment.

This completes the serverless part of the ingestion pipeline. 