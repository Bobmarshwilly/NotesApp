from datetime import datetime, timedelta
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from notes_app.database.models import User
from notes_app.database.models import get_session
from notes_app.database.repositories.user_repo import UserRepo

SECRET_KEY = "5a753cd077c5a424cff7bab5d8d5fdd8ed46f41ade877465ffa56ae447682f4d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_user_repo(session: Annotated[Session, Depends(get_session)]):
    return UserRepo(session=session)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
) -> User:
    credentials_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exeption
    except JWTError:
        raise credentials_exeption

    user = user_repo.get_user(username=username)
    if user is None:
        raise credentials_exeption
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
