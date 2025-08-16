from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from notes_app.infrastructure.database.models.user_table import User


class UserRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_user(self, user: User) -> None:
        self._session.add(user)

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
