from typing import List

from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


engine = create_engine("sqlite:///src/notes_app/database/notes_app_database.db")
session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session():
    with session_factory() as session:
        yield session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(31), unique=True)
    hashed_password: Mapped[str]

    notes: Mapped[List["Note"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username='{self.username!r}')"


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String(255))

    user: Mapped[List["User"]] = relationship(back_populates="notes")

    def __repr__(self) -> str:
        return f'Note(id={self.id!r}, content="{self.content!r}")'


@dataclass(frozen=True)
class NoteAdded:
    user: str
    content: str

    @property
    def message(self) -> str:
        return f"{self.user} added note: {self.content}"
