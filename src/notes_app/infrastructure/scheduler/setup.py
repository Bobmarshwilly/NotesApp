from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from notes_app.infrastructure.scheduler.task import delete_old_notes_task
from apscheduler.triggers.cron import CronTrigger
from notes_app.infrastructure.kafka_services.producer import KafkaProducer

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(delete_old_notes_task, CronTrigger(hour=0, minute=0))
    scheduler.start()

    producer = KafkaProducer()
    await producer.start()

    try:
        yield
    finally:
        await producer.stop()

        scheduler.shutdown(wait=False)
