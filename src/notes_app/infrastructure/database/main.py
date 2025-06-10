from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from dotenv import load_dotenv


load_dotenv()


from notes_app.infrastructure.config import config  # noqa: E402


DATABASE_URL = config.DB_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)
async_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
