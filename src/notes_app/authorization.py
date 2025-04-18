from passlib.context import CryptContext
from pydantic import BaseModel


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": "$2b$12$nWFOxaM5V.eNUWu0SzZMMODkeYk0nq8.XTPGBFC3cc/ddYsNIeNzO" # password: secret
    }
}


class User(BaseModel):
    username: str
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Authorization:
    @staticmethod
    def get_password_hash(plain_password):
        return pwd_context.hash(plain_password)
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_user(db, username: str):
        if username in db:
            user_dict = db[username]
            return User(**user_dict)
        
    @staticmethod
    def authenticate_user(username: str, password: str):
        user = Authorization.get_user(fake_users_db, username)
        if not user:
            return False
        if not Authorization.verify_password(password, user.hashed_password):
            return False
        return True
