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


def get_session():
    yield async_session()


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
