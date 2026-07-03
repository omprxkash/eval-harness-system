from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "review_automation",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.analyze"],
)

celery_app.conf.update(
    task_serializer="json",
    task_default_queue="default",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "weekly-report-monday-8am": {
            "task": "app.tasks.analyze.generate_weekly_report",
            "schedule": crontab(hour=8, minute=0, day_of_week=1),
        }
    },
)
