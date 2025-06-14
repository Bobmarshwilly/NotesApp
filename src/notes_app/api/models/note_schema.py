from typing import Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass


class NoteCreate(BaseModel):
    content: Annotated[str, Field(min_length=1, max_length=256)]


class NoteResponse(BaseModel):
    id: int
    content: str

    model_config = ConfigDict(from_attributes=True)


class NoteUpdate(BaseModel):
    content: Annotated[Optional[str], Field(None, min_length=1, max_length=256)]


class NoteID(BaseModel):
    id: int


# Класс для отправки сообщения в Kafka
@dataclass(frozen=True)
class NoteAdded:
    username: str
    content: str

    @property
    def message(self) -> str:
        return f"User {self.username} added note: {self.content}"
