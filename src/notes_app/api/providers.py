from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from notes_app.infrastructure.database.main import async_session
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.infrastructure.kafka_services.notifier import Notifier
from aiokafka import AIOKafkaProducer
from notes_app.infrastructure.kafka_services.producer import KafkaProducer
from notes_app.infrastructure.database.repositories.user_repo import UserRepo
from notes_app.infrastructure.database.repositories.note_repo import NoteRepo
from notes_app.infrastructure.redis_services.cache_manager import CacheManager
from notes_app.infrastructure.redis_services.redis_client import (
    AsyncRedis,
    async_redis_client,
)


async def get_session():
    try:
        yield async_session()
    finally:
        await async_session().close()


def get_redis_client():
    yield async_redis_client


def get_tx_manager(session: Annotated[AsyncSession, Depends(get_session)]) -> TxManager:
    return TxManager(session)


def get_notifier(
    producer: Annotated[AIOKafkaProducer, Depends(KafkaProducer.get_producer)],
) -> Notifier:
    return Notifier(producer=producer)


def get_user_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> UserRepo:
    return UserRepo(session=session)


def get_note_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> NoteRepo:
    return NoteRepo(session=session)


def get_cache_manager(
    async_client: Annotated[AsyncRedis, Depends(get_redis_client)],
) -> CacheManager:
    return CacheManager(redis_client=async_client)
