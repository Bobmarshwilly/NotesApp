import logging
from notes_app.infrastructure.database.models.note_table import Note
from notes_app.api.models.note_schema import (
    NoteCreate,
    NoteID,
    NoteResponse,
    NoteUpdate,
)
from notes_app.application.note.note_exceptions import NoAccessToNote, NoteNotFound
from notes_app.infrastructure.database.models.user_table import User
from notes_app.infrastructure.database.repositories.note_repo import NoteRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.infrastructure.kafka_services.notifier import Notifier, NoteAddedEvent
from notes_app.infrastructure.mongo_services.repositories.mongo_repo import (
    MongoNoteRepo,
)

logger = logging.getLogger(__name__)


async def create_note(
    note: NoteCreate,
    note_repo: NoteRepo,
    tx_manager: TxManager,
    mongo_note_repo: MongoNoteRepo,
    notifier: Notifier,
    current_user: User,
) -> NoteResponse:
    try:
        new_note: Note = Note(owner_id=current_user.id, content=note.content)
        await note_repo.add_note(new_note)
        await tx_manager.commit()
        await mongo_note_repo.create_note(new_note)
        event = NoteAddedEvent(username=current_user.username, content=new_note.content)
        await notifier.publish(event)
        return NoteResponse(id=new_note.id, content=new_note.content)
    except Exception:
        await tx_manager.rollback()
        raise


async def note_request(
    note_id: int, note_repo: NoteRepo, current_user: User
) -> Note | None:
    try:
        note_response = await note_repo.get_note_by_id(note_id=note_id)
        if not note_response:
            raise NoteNotFound()
        if note_response.owner_id != current_user.id:
            raise NoAccessToNote()
        return note_response
    except Exception:
        raise


async def get_note_of_current_user_by_id(
    note: NoteID, note_repo: NoteRepo, current_user: User
) -> NoteResponse:
    try:
        current_note = await note_request(
            note_id=note.id, note_repo=note_repo, current_user=current_user
        )
        if current_note is None:
            raise NoteNotFound("Note not found")
        return NoteResponse(id=current_note.id, content=current_note.content)
    except Exception:
        raise


async def delete_note_of_current_user_by_id(
    note: NoteID,
    note_repo: NoteRepo,
    tx_manager: TxManager,
    mongo_note_repo: MongoNoteRepo,
    current_user: User,
) -> None:
    try:
        current_note = await note_request(
            note_id=note.id, note_repo=note_repo, current_user=current_user
        )
        if not current_note:
            raise NoteNotFound("Note not found")
        if current_note.owner_id != current_user.id:
            raise NoAccessToNote("No access to this note")
        await note_repo.delete_note(note.id)
        await mongo_note_repo.delete_history_of_update(current_note)
        await tx_manager.commit()
    except Exception:
        await tx_manager.rollback()
        raise


async def update_note_of_current_user_by_id(
    note_id: NoteID,
    new_content: NoteUpdate,
    note_repo: NoteRepo,
    tx_manager: TxManager,
    mongo_note_repo: MongoNoteRepo,
    current_user: User,
) -> NoteResponse | None:
    try:
        current_note = await note_request(
            note_id=note_id.id, note_repo=note_repo, current_user=current_user
        )
        if not current_note:
            raise NoteNotFound("Note not found")
        if current_note.owner_id != current_user.id:
            raise NoAccessToNote("No access to this note")
        current_note_data = {"id": current_note.id, "content": current_note.content}

        update_data = new_content.model_dump()
        updated_note = await note_repo.update_note(
            note=current_note, update_data=update_data
        )
        await mongo_note_repo.update_note(
            current_note_data=current_note_data, new_note_data=updated_note
        )
        await tx_manager.commit()
        return NoteResponse(id=updated_note.id, content=updated_note.content)
    except NoteNotFound:
        raise NoteNotFound("Note not found")
    except Exception:
        await tx_manager.rollback()
        raise


async def get_update_history_of_note_by_id(
    note_id: NoteID,
    note_repo: NoteRepo,
    mongo_note_repo: MongoNoteRepo,
    current_user: User,
) -> list[NoteResponse] | None:
    try:
        current_note = await note_request(
            note_id=note_id.id, note_repo=note_repo, current_user=current_user
        )
        if not current_note:
            raise NoteNotFound("Note not found")
        if current_note.owner_id != current_user.id:
            raise NoAccessToNote("No access to this note")
        note_update_history = await mongo_note_repo.get_history_of_update(current_note)
        if not note_update_history:
            raise NoteNotFound("No update history found for this note")
        result = []
        for note in note_update_history:
            response = NoteResponse(id=note.note_id, content=note.content)
            result.append(response)
        return result
    except Exception:
        raise
