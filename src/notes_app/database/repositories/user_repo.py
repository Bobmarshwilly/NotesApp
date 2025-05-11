from sqlalchemy import select
from sqlalchemy.orm import Session
from notes_app.database.models import User


class UserRepo:
    def __init__(self, session: Session):
        self._session = session

    def add_user(self, user: User):
        self._session.add(user)

    def get_user(self, username: str):
        stmt = select(User).where(User.username == username)
        result = self._session.execute(stmt)
        user = result.scalar_one_or_none()
        return user
