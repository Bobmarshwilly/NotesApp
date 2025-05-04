from notes_app.database.models import engine, Note
from sqlalchemy.orm import Session
from sqlalchemy import delete

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def schedule_task():
    with Session(engine) as session:
        try:
            session.execute(delete(Note))
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


scheduler_task = BackgroundScheduler()
scheduler_task.add_job(schedule_task, CronTrigger(hour=0, minute=0))
