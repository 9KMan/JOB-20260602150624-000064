"""Celery application configuration."""

from celery import Celery

from src.config import get_settings

settings = get_settings()

celery_app = Celery(
    "premium_service_directory",
    broker=settings.celery.celery_broker_url,
    backend=settings.celery.celery_result_backend,
    include=[
        "src.workers.tasks",
        "src.workers.scheduled",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "src.workers.tasks.send_email": {"queue": "notifications"},
        "src.workers.tasks.process_payment": {"queue": "payments"},
        "src.workers.tasks.index_listing": {"queue": "search"},
        "src.workers.tasks.process_image": {"queue": "media"},
    },
    beat_schedule={
        "cleanup-expired-sessions": {
            "task": "src.workers.scheduled.cleanup_expired_sessions",
            "schedule": 3600.0,
        },
        "update-listing-stats": {
            "task": "src.workers.scheduled.update_listing_stats",
            "schedule": 300.0,
        },
        "process-analytics-queue": {
            "task": "src.workers.scheduled.process_analytics_queue",
            "schedule": 60.0,
        },
        "check-listing-expiry": {
            "task": "src.workers.scheduled.check_listing_expiry",
            "schedule": 3600.0,
        },
    },
)