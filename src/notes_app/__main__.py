from src.notes_app.database.models import engine, Note
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.notes_app.scheduler import scheduler_task

from src.notes_app.authorization import Authorization

from fastapi import FastAPI, Depends, HTTPException, status


app = FastAPI()

scheduler_task.start()

app.state.authorization = False


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



@app.post("/notes", summary="Добавление заметки в БД", tags=["Заметки"], dependencies=[Depends(check_authorization_status)])
def add_note(content: str):
    with Session(engine) as session:
        new_note = Note(content=content)
        session.add(new_note)
        session.commit()
    return {"success": True, "msg": "Заметка добавлена"}


@app.get("/notes", summary="Вывод всех заметок из БД", tags=["Заметки"], dependencies=[Depends(check_authorization_status)])
def list_notes():
    with Session(engine) as session:
        stmt = select(Note.content)
        notes = session.scalars(stmt).all()
    if not notes:
        return {"msg": "Нет заметок!"}
    return {"notes": notes}
