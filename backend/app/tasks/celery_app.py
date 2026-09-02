from celery import Celery
from app.config import get_settings
import os

settings = get_settings()

celery_app = Celery(
    "alcatraz",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=[
        "app.tasks.notificaciones",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Caracas",
    enable_utc=True,
    # Reintento automático si el worker falla
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
