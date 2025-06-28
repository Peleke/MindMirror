import os

from celery import Celery


def create_celery_app() -> Celery:
    """
    Factory function to create and configure a Celery app instance.
    This prevents the app from being configured at import time, which is crucial
    for testing, allowing pytest fixtures to set the broker/backend URLs.
    """
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

    celery_app = Celery(
        "celery_worker",
        broker=redis_url,
        backend=redis_url,
        include=[
            "src.tasks.journal_tasks",
            "src.tasks.tradition_tasks",
            "src.tasks.health_tasks",
        ],
    )

    celery_app.conf.update(
        task_track_started=True,
        broker_connection_retry_on_startup=True,
    )

    return celery_app


# Instantiate the app for the application to use.
# In a test environment, pytest-celery will manage the app instance.
celery_app = create_celery_app() 