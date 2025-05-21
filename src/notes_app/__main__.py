from fastapi import FastAPI
import uvicorn
from notes_app.infrastructure.scheduler.setup import lifespan
from notes_app.api.routers import auth_routers, note_routers
from notes_app.infrastructure.kafka_services.producer import KafkaProducer


app = FastAPI(lifespan=lifespan)
app.include_router(auth_routers.router)
app.include_router(note_routers.router)


@app.on_event("startup")
async def startup():
    await KafkaProducer.get_producer()


@app.on_event("shutdown")
async def shutdown():
    await KafkaProducer().stop()


def main():
    uvicorn.run("__main__:app", reload=True)


if __name__ == "__main__":
    main()
