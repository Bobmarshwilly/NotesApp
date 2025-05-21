from pydantic import BaseModel
from dataclasses import dataclass


class NoteCreate(BaseModel):
    content: str


class NoteResponse(BaseModel):
    id: int
    content: str


# Класс для отправки сообщения в Kafka
@dataclass(frozen=True)
class NoteAdded:
    username: str
    content: str

    @property
    def message(self) -> str:
        return f"User {self.username} added note: {self.content}"
