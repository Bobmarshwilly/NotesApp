from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from notes_app.infrastructure.database.models.note_table import Note
from notes_app.infrastructure.database.models.user_table import User


class NoteRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_note(self, note: Note) -> None:
        self._session.add(note)

    async def get_note_by_id(self, note_id) -> Note | None:
        stmt = select(Note).where(Note.id == note_id)
        note = await self._session.execute(stmt)
        return note.scalar()

    async def get_notes(self, current_user: User, skip: int, limit: int) -> list[Note]:
        stmt = (
            select(Note)
            .where(Note.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        notes = await self._session.execute(stmt)
        return list(notes.scalars().all())

    async def update_note(self, note: Note, update_data: dict) -> Note:
        for key, value in update_data.items():
            if hasattr(note, key):
                setattr(note, key, value)
        return note

    async def delete_note(self, id) -> None:
        stmt = delete(Note).where(Note.id == id)
        await self._session.execute(stmt)

    async def delete_all_notes(self) -> None:
        stmt = delete(Note)
        await self._session.execute(stmt)
