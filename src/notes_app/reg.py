from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from notes_app.database.models import User
from notes_app.auth import get_password_hash
from notes_app.database.repositories.user_repo import UserRepo
from notes_app.database.tx_manager import TxManager


def get_user_by_username(
    _session: Session,
    username: str,
) -> User | None:
    stmt = select(User).where(User.username == username)
    result = _session.execute(stmt)
    return result.scalar_one_or_none()


def create_user(user_data: dict, user_repo: UserRepo, tx_manager: TxManager) -> User:
    hashed_password = get_password_hash(user_data["password"])
    user = User(username=user_data["username"], hashed_password=hashed_password)
    try:
        user_repo.add_user(user=user)
        tx_manager.commit_refresh(user=user)
        return user
    except Exception as e:
        tx_manager.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
