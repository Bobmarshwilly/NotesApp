from celery import Celery
from notes_app.infrastructure.config import config


celery_app = Celery(
    "notes_app",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["notes_app.infrastructure.scheduler.tasks"],
)

celery_app.conf.update(timezone="UTC", enable_utc=True)


from notes_app.infrastructure.scheduler.beat_schedule import beat_schedule  # noqa: E402

celery_app.conf.update(beat_schedule=beat_schedule)
