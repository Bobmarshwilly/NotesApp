from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str
