from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from notes_app.api.models.user_schema import UserCreate, UserResponse
from notes_app.api.models.auth_schema import Token
from notes_app.infrastructure.database.repositories.user_repo import UserRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.api.providers import get_user_repo, get_tx_manager
from notes_app.application.user.reg import create_user
from notes_app.application.user.auth import (
    verify_password,
    create_access_token,
    AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)


router = APIRouter(prefix="/auth", tags=["Registration and authorization"])


@router.post(
    "/registration",
    summary="Регистрация нового пользователя",
    response_model=UserResponse,
    status_code=201,
)
async def register_user(
    user_data: UserCreate,
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
    tx_manager: Annotated[TxManager, Depends(get_tx_manager)],
):
    is_username_exist = await user_repo.get_user(user_data.username)
    if is_username_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    new_user = await create_user(
        user_data=user_data, user_repo=user_repo, tx_manager=tx_manager
    )
    return new_user


@router.post(
    "/token",
    summary="Авторизация пользователя",
    response_model=Token,
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
) -> Token:
    try:
        user = await user_repo.get_user(form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        access_token_expire = timedelta(minutes=AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expire
        )
        return Token(access_token=access_token, token_type="bearer")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
