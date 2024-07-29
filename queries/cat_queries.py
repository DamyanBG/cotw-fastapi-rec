from typing import Optional
from google.cloud.firestore import FieldFilter

from db import db
from models.cat_models import NextRoundCatCreate, NextRoundCat

ncr_ref = db.collection("NextRoundCats")


async def insert_nrc(cat_data: NextRoundCatCreate) -> NextRoundCat:
    cat_data_dict = cat_data.model_dump()
    new_nrc_ref = ncr_ref.document()
    await new_nrc_ref.set(cat_data_dict)
    cat_data_dict["id"] = new_nrc_ref.id
    next_round_cat = NextRoundCat(**cat_data_dict)
    return next_round_cat


async def select_user_nrc(user_id: str) -> Optional[NextRoundCat]:
    filter_field = FieldFilter("user_id", "==", user_id)
    query = ncr_ref.where(filter=filter_field)
    docs = [doc async for doc in query.stream()]
    if not docs:
        return None
    
    nrc_doc = docs[0]
    next_round_cat = NextRoundCat(id=nrc_doc.id, **nrc_doc.to_dict())
    return next_round_cat
