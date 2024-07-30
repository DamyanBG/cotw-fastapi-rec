from fastapi import APIRouter, HTTPException, status, Depends

from models.user_models import User, UserCreate, UserId, UserUpdate
from models.credentials_models import Token, Credentials
from queries.user_queries import insert_user, select_user_by_email, delete_user, select_user_by_id, update_user
from auth.password import hash_password, validate_hashed_password
from auth.token import create_access_token, get_current_user_id


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


@user_router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete(user_id: UserId = Depends(get_current_user_id)):
    await delete_user(user_id.id)
    return "OK"


@user_router.put("/update", response_model=User)
async def update(update_data: UserUpdate, user_id: UserId = Depends(get_current_user_id)):
    current_user = await select_user_by_id(user_id.id)
    if update_data.email != current_user.email:
        existing_user = await select_user_by_email(update_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered!"
        )

    update_data.password = hash_password(update_data.password)
    updated_user = await update_user(update_data, user_id.id)
    return updated_user
    