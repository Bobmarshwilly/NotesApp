from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from notes_app.infrastructure.mongo_services.models.note_model import NoteMongo
from notes_app.infrastructure.config import config


async def get_mongo_db() -> AsyncIOMotorClient:
    client: AsyncIOMotorClient = AsyncIOMotorClient(config.MONGO_URL)
    await init_beanie(
        database=client[config.MONGO_DATABASE],  # type: ignore
        document_models=[NoteMongo],
    )
    return client
