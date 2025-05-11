from typing import Annotated
from datetime import timedelta

from notes_app.database.models import get_session, User, Note, NoteAdded
from sqlalchemy.orm import Session
from notes_app.database.repositories.note_repo import NoteRepo
from notes_app.database.repositories.user_repo import UserRepo
from notes_app.database.tx_manager import TxManager

from notes_app.scheduler import scheduler_task

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from notes_app.auth import (
    create_access_token,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from notes_app.reg import create_user, get_user_by_username
from notes_app.schemas.auth import Token
from notes_app.schemas.user import UserCreate, UserResponse
from notes_app.schemas.note import NoteCreate
import uvicorn

from notes_app.kafka_services.producer import kafka_producer
from notes_app.kafka_services.notifier import Notifier


app = FastAPI()

scheduler_task.start()


def get_tx_manager(session: Annotated[Session, Depends(get_session)]) -> TxManager:
    return TxManager(session)


def get_notifier() -> Notifier:
    return Notifier(kafka_producer)


def get_user_repo(session: Annotated[Session, Depends(get_session)]):
    return UserRepo(session=session)


def get_note_repo(session: Annotated[Session, Depends(get_session)]):
    return NoteRepo(session=session)


@app.post(
    "/register",
    summary="Регистрация нового пользователя",
    tags=["Регистрация и авторизация"],
    response_model=UserResponse,
    status_code=201,
)
def register_user(
    user_data: UserCreate,
    _session: Annotated[Session, Depends(get_session)],
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
):
    if get_user_by_username(_session, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    new_user = create_user(
        user_data=user_data.model_dump(), user_repo=user_repo, tx_manager=tx_manager
    )
    return new_user


@app.post(
    "/token",
    summary="Авторизация пользователя",
    tags=["Регистрация и авторизация"],
    response_model=Token,
)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
) -> Token:
    user = user_repo.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expire
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/notes", summary="Добавление заметки в БД", tags=["Заметки"])
def add_note(
    content: NoteCreate,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manage: Annotated[TxManager, Depends(get_tx_manager)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    note = Note(owner_id=current_user.id, content=content.content)
    note_repo.add_note(note)
    tx_manage.commit()
    event = NoteAdded(user=current_user.username, content=content.content)
    notifier.publish(event)

    return {"status": "success", "message": "Заметка успешно добавлена!"}


@app.get("/notes", summary="Вывод всех заметок из БД", tags=["Заметки"])
def list_notes(
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    notes = note_repo.get_notes(current_user=current_user)
    if not notes:
        return {"msg": "Нет заметок!"}
    return {"notes": notes}


if __name__ == "__main__":
    uvicorn.run("__main__:app", reload=True)
