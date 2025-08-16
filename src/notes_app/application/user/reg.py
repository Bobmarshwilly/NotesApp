import logging
from notes_app.infrastructure.database.models.user_table import User
from notes_app.application.user.auth import get_password_hash
from notes_app.api.models.user_schema import UserCreate, UserResponse, UserCreatedEvent
from notes_app.infrastructure.database.repositories.user_repo import UserRepo
from notes_app.infrastructure.database.tx_manager import TxManager
from notes_app.application.user.user_exceptions import UsernameAlreadyExists
from notes_app.infrastructure.kafka_services.notifier import Notifier


logger = logging.getLogger(__name__)


async def create_user(
    user_data: UserCreate,
    user_repo: UserRepo,
    tx_manager: TxManager,
    notifier: Notifier,
) -> UserResponse:
    is_username_exist = await user_repo.get_user_by_username(user_data.username)
    is_email_exist = await user_repo.get_user_by_email(user_data.email)
    if is_username_exist or is_email_exist:
        raise UsernameAlreadyExists("Username or email already exists")
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    try:
        await user_repo.add_user(user=user)
        await tx_manager.commit()
        event = UserCreatedEvent(username=user.username)
        await notifier.publish(event=event)
        return UserResponse(id=user.id, username=user.username)
    except Exception as e:
        logger.error(f"User creating error: {e}")
        await tx_manager.rollback()
        raise
