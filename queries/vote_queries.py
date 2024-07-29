from typing import Optional
from google.cloud.firestore import FieldFilter, And

from db import db 
from models.vote_models import VoteCreate, Vote


vote_ref = db.collection("Votes")


async def insert_vote(vote_data: VoteCreate) -> Vote:
    vote_dict = vote_data.model_dump()
    new_vote_ref = vote_ref.document()
    await new_vote_ref.set(vote_dict)
    vote_dict["id"] = new_vote_ref.id
    vote = Vote(**vote_dict)
    return vote


async def select_vote_by_cat_and_user(cat_id: str, user_id: str) -> Optional[Vote]:
    user_id_filter = FieldFilter("user_id", "==", user_id)
    cat_id_filter = FieldFilter("cat_id", "==", cat_id)
    composite_filter = And(filters=[user_id_filter, cat_id_filter])
    query = vote_ref.where(filter=composite_filter)
    docs = [doc async for doc in query.stream()]
    if not docs:
        return None
    
    vote_doc = docs[0]
    vote = Vote(id=vote_doc.id, **vote_doc.to_dict())
    return vote


async def select_voted_cats_ids(user_id: str) -> list[str]:
    filter_by_user_id = FieldFilter("user_id", "==", user_id)
    query = vote_ref.where(filter=filter_by_user_id)
    cats_ids = [doc.to_dict()["cat_id"] async for doc in query.stream()]
    return cats_ids
