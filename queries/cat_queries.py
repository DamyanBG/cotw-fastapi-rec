from asyncio import gather
from typing import Optional
from google.cloud.firestore import FieldFilter

from db import db
from models.cat_models import NextRoundCatCreate, NextRoundCat, CurrentRoundCatCreate

nrc_ref = db.collection("NextRoundCats")
crc_ref = db.collection("CurrentRoundCats")


async def insert_nrc(cat_data: NextRoundCatCreate) -> NextRoundCat:
    cat_data_dict = cat_data.model_dump()
    new_nrc_ref = nrc_ref.document()
    await new_nrc_ref.set(cat_data_dict)
    cat_data_dict["id"] = new_nrc_ref.id
    next_round_cat = NextRoundCat(**cat_data_dict)
    return next_round_cat


async def select_user_nrc(user_id: str) -> Optional[NextRoundCat]:
    filter_field = FieldFilter("user_id", "==", user_id)
    query = nrc_ref.where(filter=filter_field)
    docs = [doc async for doc in query.stream()]
    if not docs:
        return None
    
    nrc_doc = docs[0]
    next_round_cat = NextRoundCat(id=nrc_doc.id, **nrc_doc.to_dict())
    return next_round_cat


async def select_all_nr_cats() -> list[NextRoundCat]:
    docs = [doc async for doc in nrc_ref.stream()]
    next_round_cats = [
        NextRoundCat(id=doc.id, **doc.to_dict()) for doc in docs 
    ]
    return next_round_cats


async def delete_all_nr_cats(cats: list[NextRoundCat]) -> None:
    delete_tasks = [nrc_ref.document(cat.id).delete() for cat in cats]
    await gather(*delete_tasks)


async def insert_current_round_cats(cats: list[CurrentRoundCatCreate]) -> None:
    cats_dicts = [cat.model_dump() for cat in cats]
    new_cats_refs = [
        crc_ref.document() for _ in range(len(cats_dicts))
    ]
    insert_operations = [
        new_cat_ref.set(cat_dict) for cat_dict, new_cat_ref in zip(cats_dicts, new_cats_refs)
    ]
    await gather(*insert_operations)
