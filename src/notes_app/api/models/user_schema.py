from typing import Annotated
from pydantic import BaseModel, Field, EmailStr
from dataclasses import dataclass


class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=32)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class UserResponse(BaseModel):
    id: int
    username: str


@dataclass
class UserCreatedEvent:
    username: str

    @property
    def message(self) -> str:
        return f"New user was created. Username: {self.username}"
