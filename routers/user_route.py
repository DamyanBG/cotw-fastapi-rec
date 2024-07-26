from fastapi import APIRouter, HTTPException, status

from models.user_models import User, UserCreate
from models.credentials_models import Token, Credentials
from queries.user_queries import insert_user, select_user_by_email
from auth.password import hash_password, validate_hashed_password
from auth.token import create_access_token


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/register", response_model=User)
async def create_user(user_data: UserCreate):
    existing_user = await select_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered!",
        )

    user_data.password = hash_password(user_data.password)
    new_user = await insert_user(user_data)
    return new_user


@user_router.post("/login", response_model=Token)
async def login_user(credentials: Credentials):
    existing_user = await select_user_by_email(credentials.email)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad credentials!"
        )

    if not validate_hashed_password(existing_user.password, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad credentials!"
        )

    token = create_access_token(existing_user)

    return {"token": token}
