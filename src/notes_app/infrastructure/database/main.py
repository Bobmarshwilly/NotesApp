from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker


engine = create_async_engine(
    "sqlite+aiosqlite:///src/notes_app/infrastructure/database/notes_app_database.db",
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
)
async_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
