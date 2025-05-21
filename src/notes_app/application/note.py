from notes_app.infrastructure.database.models.note_table import Note
from notes_app.api.models.note_schema import NoteCreate
from notes_app.infrastructure.database.models.user_table import User
from notes_app.infrastructure.database.repositories.note_repo import NoteRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.infrastructure.kafka_services.notifier import Notifier, NoteAdded
from fastapi import HTTPException, status


async def create_note(
    note: NoteCreate,
    note_repo: NoteRepo,
    tx_manager: TxManager,
    notifier: Notifier,
    current_user: User,
):
    try:
        note = Note(owner_id=current_user.id, content=note.content)
        await note_repo.add_note(note)
        await tx_manager.commit()
        event = NoteAdded(username=current_user.username, content=note.content)
        await notifier.publish(event)
    except Exception:
        await tx_manager.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note",
        )
