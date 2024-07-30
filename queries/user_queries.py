from typing import Optional
from google.cloud.firestore import FieldFilter

from db import db
from models.user_models import UserCreate, User, UserUpdate


user_ref = db.collection("Users")


async def insert_user(user: UserCreate) -> User:
    user_data = user.model_dump()
    new_user_ref = user_ref.document()
    await new_user_ref.set(user_data)
    user_data["id"] = new_user_ref.id
    new_user = User(**user_data)
    return new_user


async def select_user_by_email(email: str) -> Optional[User]:
    filter_by_email = FieldFilter("email", "==", email)
    query = user_ref.where(filter=filter_by_email)
    user_docs = [doc async for doc in query.stream()]
    if user_docs:
        user_doc = user_docs[0]
        user_data = user_doc.to_dict()
        user_data["id"] = user_doc.id
        user = User(**user_data)
        return user

    return None


async def delete_user(user_id: str) -> None:
    user_doc_ref = user_ref.document(user_id)
    await user_doc_ref.delete()


async def check_user_exists(user_id: str) -> bool:
    user_doc_ref = user_ref.document(user_id)
    user_doc = await user_doc_ref.get()
    user_exists = user_doc.exists
    return user_exists


async def select_user_by_id(user_id: str) -> User:
    user_doc_ref = user_ref.document(user_id)
    user_doc = await user_doc_ref.get()
    user = User(
        id=user_doc.id, **user_doc.to_dict()
    )
    return user


async def update_user(update_data: UserUpdate, user_id: str) -> User:
    user_doc_ref = user_ref.document(user_id)
    update_data_dict = update_data.model_dump()
    await user_doc_ref.update(update_data_dict)
    updated_user = User(
        id=user_id, **update_data_dict
    )
    return updated_user
