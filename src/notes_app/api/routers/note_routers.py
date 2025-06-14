import logging
from redis.exceptions import RedisError
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from notes_app.api.providers import (
    get_note_repo,
    get_notifier,
    get_tx_manager,
    get_cache_manager,
)
from notes_app.api.models.note_schema import (
    NoteCreate,
    NoteResponse,
    NoteID,
    NoteUpdate,
)
from notes_app.infrastructure.database.repositories.note_repo import NoteRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.infrastructure.kafka_services.notifier import Notifier
from notes_app.infrastructure.database.models.user_table import User
from notes_app.infrastructure.redis_services.cache_manager import CacheManager
from notes_app.application.note.note import (
    create_note,
    delete_note_of_current_user_by_id,
    get_note_of_current_user_by_id,
    update_note_of_current_user_by_id,
)
from notes_app.application.note.note_exceptions import NoAccessToNote, NoteNotFound
from notes_app.application.user.auth import get_current_user


router = APIRouter(prefix="/note", tags=["Notes"])

logger = logging.getLogger(__name__)


@router.post("/create", summary="Добавление заметки в БД", response_model=NoteResponse)
async def add_note(
    note: NoteCreate,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
    current_user: Annotated[User, Depends(get_current_user)],
    cache_manager: Annotated[CacheManager, Depends(get_cache_manager)],
):
    try:
        new_note = await create_note(
            note=note,
            note_repo=note_repo,
            tx_manager=tx_manager,
            notifier=notifier,
            current_user=current_user,
        )

        await cache_manager.delete_pattern(f"notes:owner_id={current_user.id}:*")

        return new_note
    except RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {type(e).__name__} - {str(e)}")
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
    cache_manager: Annotated[CacheManager, Depends(get_cache_manager)],
    skip: int = 0,
    limit: int = 10,
):
    try:
        cache_key = await cache_manager.generate_key(
            "notes", f"owner_id={current_user.id}", f"skip={skip}", f"limit={limit}"
        )
        if cached := await cache_manager.get(cache_key):
            return cached

        notes_response = await note_repo.get_notes(
            current_user=current_user, skip=skip, limit=limit
        )
        if not notes_response:
            raise NoteNotFound()
        notes = [NoteResponse.model_validate(n) for n in notes_response]
        notes_data = [note.model_dump() for note in notes]
        await cache_manager.set(cache_key, notes_data)
        return notes
    except NoteNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="List of notes is empty"
        )
    except RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list notes",
        )


@router.get("/{note_id}", summary="Вывод заметки по id", response_model=NoteResponse)
async def get_note(
    note_id: int,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
    cache_manager: Annotated[CacheManager, Depends(get_cache_manager)],
):
    try:
        cache_key = await cache_manager.generate_key(
            "notes", f"owner_id={current_user.id}", f"note_id={note_id}"
        )
        if cached := await cache_manager.get(cache_key):
            return cached

        note = NoteID(id=note_id)
        note_request = await get_note_of_current_user_by_id(
            note, note_repo, current_user
        )

        await cache_manager.set(cache_key, note_request.model_dump())
        return note_request
    except NoAccessToNote:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to note",
        )
    except NoteNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    except RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note",
        )


@router.patch(
    "/{note_id}/update",
    summary="Обновление содержимого заметки по id",
    response_model=NoteResponse,
)
async def update_note_by_id(
    note_id: int,
    new_content: NoteUpdate,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
    current_user: Annotated[User, Depends(get_current_user)],
    cache_manager: Annotated[CacheManager, Depends(get_cache_manager)],
):
    try:
        _note_id = NoteID(id=note_id)
        updated_note = await update_note_of_current_user_by_id(
            note_id=_note_id,
            new_content=new_content,
            note_repo=note_repo,
            tx_manager=tx_manager,
            current_user=current_user,
        )

        cache_key = await cache_manager.generate_key(
            "notes", f"owner_id={current_user.id}", f"note_id={note_id}"
        )
        await cache_manager.delete(cache_key)
        await cache_manager.delete_pattern(f"notes:owner_id={current_user.id}:*")

        return updated_note
    except NoAccessToNote:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to note",
        )
    except NoteNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    except RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update note",
        )


@router.post("/{note_id}/delete", summary="Удаление заметки по id")
async def delete_note_by_id(
    note_id: int,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
    current_user: Annotated[User, Depends(get_current_user)],
    cache_manager: Annotated[CacheManager, Depends(get_cache_manager)],
):
    try:
        note = NoteID(id=note_id)
        await delete_note_of_current_user_by_id(
            note, note_repo, tx_manager, current_user
        )

        cache_key = await cache_manager.generate_key(
            "notes", f"owner_id={current_user.id}", f"note_id={note_id}"
        )
        await cache_manager.delete(cache_key)
        await cache_manager.delete_pattern(f"notes:owner_id={current_user.id}:*")

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
    except RedisError as e:
        logger.error(f"Redis error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note",
        )
