from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from notes_app.api.providers import get_note_repo, get_notifier, get_tx_manager
from notes_app.api.models.note_schema import NoteCreate, NoteResponse, NoteID
from notes_app.infrastructure.database.repositories.note_repo import NoteRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.infrastructure.kafka_services.notifier import Notifier
from notes_app.infrastructure.database.models.user_table import User
from notes_app.application.note.note import (
    create_note,
    delete_note_of_current_user_by_id,
    get_note_of_current_user_by_id,
)
from notes_app.application.note.note_exceptions import NoAccessToNote, NoteNotFound
from notes_app.application.user.auth import get_current_user


router = APIRouter(prefix="/note", tags=["Notes"])


@router.post("/create", summary="Добавление заметки в БД")
async def add_note(
    note: NoteCreate,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        await create_note(
            note=note,
            note_repo=note_repo,
            tx_manager=tx_manager,
            notifier=notifier,
            current_user=current_user,
        )
        return {"status": "success", "message": "Заметка успешно добавлена!"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note",
        )


@router.get(
    "/notes", summary="Вывод всех заметок из БД", response_model=list[NoteResponse]
)
async def list_notes(
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        notes = await note_repo.get_notes(current_user=current_user)
        return notes
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list notes",
        )


@router.get("/{note_id}", summary="Вывод заметки по id", response_model=NoteResponse)
async def get_note(
    note_id: int,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    note = NoteID(id=note_id)
    try:
        return await get_note_of_current_user_by_id(note, note_repo, current_user)
    except NoAccessToNote:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to note",
        )
    except NoteNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note",
        )


@router.post("/{note_id}/delete", summary="Удаление заметки по id")
async def delete_note_by_id(
    note_id: int,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    note = NoteID(id=note_id)
    try:
        await delete_note_of_current_user_by_id(
            note, note_repo, tx_manager, current_user
        )
        return {"status": "success", "message": "Заметка успешно удалена!"}
    except NoAccessToNote:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to delete a note",
        )
    except NoteNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note",
        )
