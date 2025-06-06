from notes_app.infrastructure.database.models.note_table import Note
from notes_app.api.models.note_schema import NoteCreate, NoteID, NoteResponse
from notes_app.application.note.note_exceptions import NoAccessToNote, NoteNotFound
from notes_app.infrastructure.database.models.user_table import User
from notes_app.infrastructure.database.repositories.note_repo import NoteRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.infrastructure.kafka_services.notifier import Notifier, NoteAdded


async def create_note(
    note: NoteCreate,
    note_repo: NoteRepo,
    tx_manager: TxManager,
    notifier: Notifier,
    current_user: User,
) -> None:
    try:
        new_note: Note = Note(owner_id=current_user.id, content=note.content)
        await note_repo.add_note(new_note)
        await tx_manager.commit()
        event = NoteAdded(username=current_user.username, content=new_note.content)
        await notifier.publish(event)
    except Exception:
        await tx_manager.rollback()
        raise


async def get_note_of_current_user_by_id(
    note: NoteID, note_repo: NoteRepo, current_user: User
) -> NoteResponse:
    try:
        current_note = await note_repo.get_note_by_id(note.id)
        if not current_note:
            raise NoteNotFound()
        if current_note.owner_id != current_user.id:
            raise NoAccessToNote()
        return NoteResponse(id=current_note.id, content=current_note.content)
    except Exception:
        raise


async def delete_note_of_current_user_by_id(
    note: NoteID, note_repo: NoteRepo, tx_manager: TxManager, current_user: User
) -> None:
    try:
        exsisting_note = await note_repo.get_note_by_id(note.id)
        if not exsisting_note:
            raise NoteNotFound()
        if exsisting_note.owner_id != current_user.id:
            raise NoAccessToNote()
        await note_repo.delete_note(note.id)
        await tx_manager.commit()
    except Exception:
        await tx_manager.rollback()
        raise
