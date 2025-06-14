from sqlalchemy import delete
from sqlalchemy.orm import Session
from notes_app.infrastructure.database.models.note_table import Note


class CeleryRepo:
    def __init__(self, session: Session):
        self._session = session

    def delete_all_notes(self) -> None:
        stmt = delete(Note)
        self._session.execute(stmt)
