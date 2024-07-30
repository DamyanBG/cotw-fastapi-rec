import jwt
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import JWT_KEY
from models.user_models import User, UserId
from queries.user_queries import check_user_exists

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


async def verify_token(token: str, credentials_exception: HTTPException) -> UserId:
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
        if not await check_user_exists(user_id_str):
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user_id = UserId(id=user_id_str)
    return user_id


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UserId:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return await verify_token(token, credentials_exception)
    