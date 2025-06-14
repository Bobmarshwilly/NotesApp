from celery.schedules import crontab


beat_schedule = {
    "delete-old-notes-daily": {
        "task": "notes_app.infrastructure.scheduler.tasks.delete_old_notes_task",
        "schedule": crontab(hour=0, minute=0),
        "options": {"queue": "scheduler"},
    }
}
