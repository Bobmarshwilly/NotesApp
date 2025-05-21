from typing import List, TYPE_CHECKING
from notes_app.infrastructure.database.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


if TYPE_CHECKING:
    from notes_app.infrastructure.database.models.user_table import User


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String(255))

    user: Mapped[List["User"]] = relationship(back_populates="notes")

    def __repr__(self) -> str:
        return f'Note(id={self.id!r}, content="{self.content!r}")'
