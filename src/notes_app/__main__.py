from typing import Annotated

from notes_app.database.models import engine, session_factory, Note, NoteAdded
from sqlalchemy.orm import Session
from notes_app.database.repositories.note_repo import NoteRepo

from notes_app.scheduler import scheduler_task

from notes_app.authorization import Authorization

from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn

from notes_app.kafka_services.producer import kafka_producer
from notes_app.kafka_services.config import TOPIC_NAMES
from notes_app.kafka_services.notifier import Notifier


app = FastAPI()

scheduler_task.start()

app.state.authorization = False


def get_session():
    with session_factory() as session:
        yield session


def get_note_repo(session: Annotated[Session, Depends(get_session)]):
    return NoteRepo(session=session)


def get_authorization():
    return Authorization


def check_authorization_status():
    if not app.state.authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
        )


@app.post("/login", summary="Авторизация", tags=["Авторизация"])
def login_in(
    username: str,
    password: str,
    authorization: Annotated[Authorization, Depends(get_authorization)],
):
    authorization_status = authorization.authenticate_user(username=username, password=password)
    print(authorization_status)
    if not authorization_status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    app.state.authorization = True
    return {"authorization": "success"}


class TxManager:
    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()


def get_tx_manager(session: Annotated[Session, Depends(get_session)]) -> TxManager:
    return TxManager(session)


def get_notifier() -> Notifier:
    return Notifier(kafka_producer)


@app.post("/notes", summary="Добавление заметки в БД", tags=["Заметки"])
def add_note(
    content: str,
    note_repo: Annotated[NoteRepo, Depends(get_note_repo)],
    tx_manage: Annotated[TxManager, Depends(get_tx_manager)],
    notifier: Annotated[Notifier, Depends(get_notifier)],
):
    check_authorization_status()
    note = Note(content=content)
    note_repo.add_note(note)
    tx_manage.commit()
    event = NoteAdded(user="johndoe", content=content)
    notifier.publish(event)

    return {"status": "success", "message": "Заметка успешно добавлена!"}


@app.get("/notes", summary="Вывод всех заметок из БД", tags=["Заметки"])
def list_notes(note_repo: Annotated[NoteRepo, Depends(get_note_repo)]):
    check_authorization_status()
    notes = note_repo.get_notes()
    if not notes:
        return {"msg": "Нет заметок!"}
    return {"notes": notes}


if __name__ == "__main__":
    uvicorn.run("__main__:app", reload=True)
