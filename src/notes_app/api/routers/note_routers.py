from typing import Annotated
from fastapi import APIRouter, Depends
from notes_app.api.providers import get_note_repo, get_notifier, get_tx_manager
from notes_app.api.models.note_schema import NoteCreate, NoteResponse
from notes_app.infrastructure.database.repositories.note_repo import NoteRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.infrastructure.kafka_services.notifier import Notifier
from notes_app.infrastructure.database.models.user_table import User
from notes_app.application.note import create_note
from notes_app.application.user.auth import get_current_user


router = APIRouter(prefix="/note", tags=["Notes"])


@router.post("/notes", summary="Добавление заметки в БД")
async def add_note(
    note: NoteCreate,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    await create_note(
        note=note,
        note_repo=note_repo,
        tx_manager=tx_manager,
        notifier=notifier,
        current_user=current_user,
    )
    return {"status": "success", "message": "Заметка успешно добавлена!"}


@router.get(
    "/notes", summary="Вывод всех заметок из БД", response_model=list[NoteResponse]
)
async def list_notes(
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    notes = await note_repo.get_notes(current_user=current_user)
    return notes
