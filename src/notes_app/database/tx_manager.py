from sqlalchemy.orm import Session
from notes_app.database.models import User


class TxManager:
    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def commit_refresh(self, user: User) -> None:
        self._session.commit()
        self._session.refresh(user)

    def rollback(self) -> None:
        self._session.rollback()
