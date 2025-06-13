import os
import logging
import requests
import functions_framework
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

@functions_framework.cloud_event
def trigger_reindex_on_gcs_upload(cloud_event):
    """
    Cloud Function triggered by a new file upload to a GCS bucket.
    
    This function extracts the 'tradition' from the file's path and
    calls a secure webhook to trigger a re-indexing task.
    """
    # Get environment variables
    api_webhook_url = os.environ.get("API_WEBHOOK_URL")
    reindex_secret = os.environ.get("REINDEX_SECRET_KEY")

    if not all([api_webhook_url, reindex_secret]):
        logging.error("Missing required environment variables: API_WEBHOOK_URL or REINDEX_SECRET_KEY.")
        return ("Configuration error", 500)

    # Get file metadata from the event
    data = cloud_event.data
    bucket = data.get("bucket")
    file_name = data.get("name")

    if not all([bucket, file_name]):
        logging.error("Invalid CloudEvent payload. Missing 'bucket' or 'name'.")
        return ("Bad Request", 400)

    logging.info(f"Received event for file: gs://{bucket}/{file_name}")

    # The tradition is the top-level directory in the file path
    # e.g., "canon-default/documents/some_book.pdf" -> "canon-default"
    try:
        tradition = file_name.split('/')[0]
    except IndexError:
        logging.error(f"Could not determine tradition from file path: {file_name}")
        return ("Bad Request", 400)

    logging.info(f"Triggering re-indexing for tradition: {tradition}")

    # Prepare and send the request to the webhook
    headers = {"X-Reindex-Secret": reindex_secret}
    params = {"tradition": tradition}

    try:
        response = requests.post(api_webhook_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Raises an exception for 4xx/5xx errors
        
        logging.info(f"Successfully triggered webhook. Status: {response.status_code}, Response: {response.text}")
        return ("Webhook triggered successfully", 200)

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to call webhook: {e}")
        return ("Webhook call failed", 500) 