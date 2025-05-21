from typing import Annotated
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=32)]
    password: Annotated[str, Field(min_length=8)]


class UserResponse(BaseModel):
    id: int
    username: str
