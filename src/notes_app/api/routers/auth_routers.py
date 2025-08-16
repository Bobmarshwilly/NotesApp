import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from notes_app.api.models.user_schema import UserCreate, UserResponse
from notes_app.api.models.auth_schema import Token
from notes_app.infrastructure.database.repositories.user_repo import UserRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.api.providers import get_user_repo, get_tx_manager, get_notifier
from notes_app.application.user.reg import create_user
from notes_app.application.user.auth import (
    authenticate_user,
)
from notes_app.application.user.user_exceptions import (
    UsernameAlreadyExists,
    InvalidCredentialsError,
)
from notes_app.infrastructure.kafka_services.notifier import Notifier


logger = logging.getLogger(__name__)

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
    notifier: Annotated[Notifier, Depends(get_notifier)],
) -> UserResponse:
    try:
        new_user = await create_user(
            user_data=user_data,
            user_repo=user_repo,
            tx_manager=tx_manager,
            notifier=notifier,
        )
        return new_user
    except UsernameAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


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
        access_token = await authenticate_user(
            form_data.username, form_data.password, user_repo=user_repo
        )
        return Token(access_token=access_token, token_type="bearer")
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
