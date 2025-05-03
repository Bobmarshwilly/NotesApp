from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


engine = create_engine("sqlite:///src/notes_app/database/notes_app_database.db")
session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f'Note(id={self.id}, content="{self.content}")'
    

@dataclass(frozen=True)
class NoteAdded:
    user: str
    content: str

    @property
    def message(self) -> str:
        return f"{self.user} added note: {self.content}"