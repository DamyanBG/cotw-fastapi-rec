import jwt
from datetime import datetime, timedelta, UTC
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from config import JWT_KEY
from models.user_models import User

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "exp": datetime.now(UTC) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    }
    encoded_jwt = jwt.encode(payload, JWT_KEY, algorithm=ALGORITHM)
    return encoded_jwt
