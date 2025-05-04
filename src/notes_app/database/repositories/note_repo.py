from sqlalchemy import select
from sqlalchemy.orm import Session
from notes_app.database.models import Note


class NoteRepo:
    def __init__(self, session: Session):
        self._session = session

    def add_note(self, note: Note):
        self._session.add(note)

    def get_notes(self) -> list[Note]:
        stmt = select(Note.content)
        notes = self._session.scalars(stmt).all()
        return notes
