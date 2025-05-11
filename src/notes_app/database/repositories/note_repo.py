from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session
from notes_app.database.models import Note, User


class NoteRepo:
    def __init__(self, session: Session):
        self._session = session

    def add_note(self, note: Note) -> None:
        self._session.add(note)

    def get_notes(self, current_user: User) -> Sequence[str]:
        stmt = select(Note.content).where(Note.owner_id == current_user.id)
        notes = self._session.scalars(stmt).all()
        return notes
