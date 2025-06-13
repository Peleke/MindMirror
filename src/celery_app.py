import os
from celery import Celery

# Get the Redis connection string from the environment variable
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Define the Celery application instance
celery_app = Celery(
    "librarian_ai",
    broker=redis_url,
    backend=redis_url,
    include=[
        "src.tasks",
        "ingestion.tasks.rebuild_tradition",
    ]
)

# Optional: Configure Celery for better debugging or production settings
celery_app.conf.update(
    task_track_started=True,
    broker_connection_retry_on_startup=True,
) 