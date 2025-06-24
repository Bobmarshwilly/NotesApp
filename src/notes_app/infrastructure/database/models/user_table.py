from typing import List, TYPE_CHECKING
from notes_app.infrastructure.database.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String


if TYPE_CHECKING:
    from notes_app.infrastructure.database.models.note_table import Note


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(31), unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]

    notes: Mapped[List["Note"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username='{self.username!r}')"
