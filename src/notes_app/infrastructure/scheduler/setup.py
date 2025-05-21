from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from notes_app.infrastructure.scheduler.task import delete_old_notes_task
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(delete_old_notes_task, CronTrigger(hour=0, minute=0))

    try:
        scheduler.start()
        yield
    finally:
        scheduler.shutdown(wait=False)
