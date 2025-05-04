from passlib.context import CryptContext
from pydantic import BaseModel


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": "$2b$12$nWFOxaM5V.eNUWu0SzZMMODkeYk0nq8.XTPGBFC3cc/ddYsNIeNzO",  # password: secret
    }
}


class User(BaseModel):
    username: str
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Authorization:
    def get_password_hash(self, plain_password):
        return pwd_context.hash(plain_password)

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_user(self, db, username: str):
        if username in db:
            user_dict = db[username]
            return User(**user_dict)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(fake_users_db, username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return True
