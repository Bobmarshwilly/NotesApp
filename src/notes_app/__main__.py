from typing import Annotated

from notes_app.database.models import engine, Note
from sqlalchemy import select
from sqlalchemy.orm import Session

from notes_app.scheduler import scheduler_task

from notes_app.authorization import Authorization

from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn


app = FastAPI()

scheduler_task.start()

app.state.authorization = False


class NoteRepo:
    def __init__(self, session: Session):
        self._session = session

    def get_notes(self) -> list[Note]:
        stmt = select(Note.content)
        notes = self._session.scalars(stmt).all()
        return notes


def get_note_repo():
    note_repo = NoteRepo(session=Session(engine))
    return note_repo


def check_authorization_status():
    if not app.state.authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
        )


@app.post("/login", summary="Авторизация", tags=["Авторизация"])
def login_in(username: str, password: str):
    user = Authorization.authenticate_user(username=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    app.state.authorization = True
    return {"authorization": "success"}



@app.post("/notes", summary="Добавление заметки в БД", tags=["Заметки"])
def add_note(content: str):
    check_authorization_status()
    with Session(engine) as session:
        new_note = Note(content=content)
        session.add(new_note)
        session.commit()
    return {"success": True, "msg": "Заметка добавлена"}


@app.get("/notes", summary="Вывод всех заметок из БД", tags=["Заметки"])
def list_notes(note_repo: Annotated[NoteRepo, Depends(get_note_repo)]):
    check_authorization_status()
    notes = note_repo.get_notes()
    if not notes:
        return {"msg": "Нет заметок!"}
    return {"notes": notes}


if __name__ == "__main__":
    uvicorn.run("__main__:app", reload=True)
