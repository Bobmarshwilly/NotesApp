from sqlalchemy import create_engine

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


engine = create_engine("sqlite:///src/notes_app/database/notes_app_database.db")


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f'Note(id={self.id}, content="{self.content}")'