from fastapi import HTTPException, status
from notes_app.infrastructure.database.models.user_table import User
from notes_app.application.user.auth import get_password_hash
from notes_app.api.models.user_schema import UserCreate, UserResponse
from notes_app.infrastructure.database.repositories.user_repo import UserRepo
from notes_app.infrastructure.database.tx_manager import TxManager


async def create_user(
    user_data: UserCreate, user_repo: UserRepo, tx_manager: TxManager
) -> UserResponse:
    hashed_password = get_password_hash(user_data.password)
    user = User(username=user_data.username, hashed_password=hashed_password)
    try:
        await user_repo.add_user(user=user)
        await tx_manager.commit()
        return user
    except Exception as e:
        await tx_manager.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
