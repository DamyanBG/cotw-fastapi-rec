from fastapi import APIRouter, HTTPException, status

from models.user_models import User, UserCreate
from queries.user_queries import insert_user, select_user_by_email
from auth.password import hash_password


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/register", response_model=User)
async def create_user(user_data: UserCreate):
    existing_user = await select_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Email is already registered!'
        )
    
    user_data.password = hash_password(user_data.password)
    new_user = await insert_user(user_data)
    return new_user
