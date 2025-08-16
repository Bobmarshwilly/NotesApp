from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from notes_app.api.routers import auth_routers, note_routers
from notes_app.infrastructure.kafka_services.producer import KafkaProducer
from notes_app.infrastructure.mongo_services.mongo_client import get_mongo_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = KafkaProducer()
    await producer.start()
    await get_mongo_db()

    try:
        yield
    finally:
        await producer.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_routers.router)
app.include_router(note_routers.router)


def main():
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
