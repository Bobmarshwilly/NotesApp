from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from notes_app.infrastructure.config import config


async_engine = create_async_engine(config.ASYNC_DB_URL, echo=True, future=True)
async_session = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)

sync_engine = create_engine(config.SYNC_DB_URL)
sync_session = sessionmaker(bind=sync_engine, autoflush=False, expire_on_commit=False)
