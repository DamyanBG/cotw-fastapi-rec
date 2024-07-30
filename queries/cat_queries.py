from asyncio import gather
from datetime import date
from typing import Optional
from google.cloud.firestore import FieldFilter, Increment, And
from google.cloud.exceptions import NotFound

from db import db
from models.cat_models import (
    NextRoundCatCreate,
    NextRoundCat,
    NextRoundCatUpdate,
    CurrentRoundCatCreate,
    CurrentRoundCat,
    CatOfTheWeekCreate,
    CatOfTheWeek,
)

nrc_ref = db.collection("NextRoundCats")
crc_ref = db.collection("CurrentRoundCats")
cat_of_the_week_ref = db.collection("CatsOfTheWeek")


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
    next_round_cats = [NextRoundCat(id=doc.id, **doc.to_dict()) for doc in docs]
    return next_round_cats


async def delete_all_nr_cats(cats: list[NextRoundCat]) -> None:
    delete_tasks = [nrc_ref.document(cat.id).delete() for cat in cats]
    await gather(*delete_tasks)


async def delete_nr_cat(user_id: str) -> None:
    user_id_filter = FieldFilter("user_id", "==", user_id)
    query = nrc_ref.where(filter=user_id_filter)
    docs = [doc async for doc in query.stream()]

    if not docs:
        raise NotFound("This user does not have a cat!")
    
    doc = docs[0]
    await nrc_ref.document(doc.id).delete()


async def update_nr_cat(new_cat_data: NextRoundCatUpdate, user_id: str) -> NextRoundCat:
    cat_to_update_doc = nrc_ref.document(new_cat_data.id)
    cat_to_update = await cat_to_update_doc.get()

    if not cat_to_update.exists:
        raise NotFound("Cat with this id is not found!")
    
    cat_to_update_user_id = cat_to_update.to_dict()["user_id"]
    if cat_to_update_user_id != user_id:
        raise Exception("This cat is not related to this user!")
    
    new_cat_data_dict = new_cat_data.model_dump()
    await cat_to_update_doc.update(new_cat_data_dict)
    updated_cat = NextRoundCat(**new_cat_data_dict, user_id=user_id)
    return updated_cat


async def delete_all_cr_cats() -> None:
    cat_ids = [doc.id async for doc in crc_ref.stream()]
    delete_tasks = [crc_ref.document(cat_id).delete() for cat_id in cat_ids]
    await gather(*delete_tasks)


async def insert_current_round_cats(cats: list[CurrentRoundCatCreate]) -> None:
    cats_dicts = [cat.model_dump() for cat in cats]
    new_cats_refs = [crc_ref.document() for _ in range(len(cats_dicts))]
    insert_operations = [
        new_cat_ref.set(cat_dict)
        for cat_dict, new_cat_ref in zip(cats_dicts, new_cats_refs)
    ]
    await gather(*insert_operations)


async def add_like(cat_id: str) -> None:
    cat_doc_ref = crc_ref.document(cat_id)
    await cat_doc_ref.update({"likes": Increment(1), "votes": Increment(1)})


async def add_dislike(cat_id: str) -> None:
    cat_doc_ref = crc_ref.document(cat_id)
    await cat_doc_ref.update({"dislikes": Increment(1), "votes": Increment(1)})


async def select_not_voted_cat(voted_cats_ids: list[str]) -> CurrentRoundCat:
    print(voted_cats_ids)
    all_cats_docs = [doc async for doc in crc_ref.stream()]
    all_cats = [
        CurrentRoundCat(id=cat_doc.id, **cat_doc.to_dict()) for cat_doc in all_cats_docs
    ]
    filtered_cats = [cat for cat in all_cats if cat.id not in voted_cats_ids]

    if not filtered_cats:
        raise NotFound("No cat for vote!")

    sorted_cats = sorted(filtered_cats, key=lambda cat: cat.votes)
    cat_for_vote = sorted_cats[0]

    return cat_for_vote


async def select_winning_cat():
    all_cats_docs = [doc async for doc in crc_ref.stream()]
    all_cats = [
        CurrentRoundCat(id=cat_doc.id, **cat_doc.to_dict()) for cat_doc in all_cats_docs
    ]
    cat_with_highest_score = max(all_cats, key=lambda cat: cat.likes - cat.dislikes)

    return cat_with_highest_score


async def insert_cat_of_the_week(cat_data: CatOfTheWeekCreate) -> None:
    cotw_dict = cat_data.model_dump()
    new_cotw_ref = cat_of_the_week_ref.document()
    await new_cotw_ref.set(cotw_dict)


async def select_cat_of_the_week() -> CatOfTheWeek:
    current_date = date.today()
    iso_calendar = current_date.isocalendar()
    week_number = iso_calendar.week
    year = iso_calendar.year

    week_filter = FieldFilter("week_number", "==", week_number)
    year_filter = FieldFilter("year", "==", year)
    composite_filter = And(filters=[week_filter, year_filter])

    query = cat_of_the_week_ref.where(filter=composite_filter)
    docs = [doc async for doc in query.stream()]
    if not docs:
        raise NotFound("No cat of the week for the current week!")
    
    cat_doc = docs[0]
    cat_of_the_week = CatOfTheWeek(
        id=cat_doc.id, **cat_doc.to_dict()
    )
    return cat_of_the_week


async def check_image_relates_to_crc(image_id: str) -> bool:
    image_id_filter = FieldFilter("photo_id", "==", image_id)
    query = crc_ref.where(filter=image_id_filter)
    docs = [doc async for doc in query.stream()]
    return bool(docs)


async def check_image_relates_to_nrc(image_id: str) -> bool:
    image_id_filter = FieldFilter("photo_id", "==", image_id)
    query = nrc_ref.where(filter=image_id_filter)
    docs = [doc async for doc in query.stream()]
    return bool(docs)


async def check_image_relates_to_cotw(image_id: str) -> bool:
    image_id_filter = FieldFilter("photo_id", "==", image_id)
    query = cat_of_the_week_ref.where(filter=image_id_filter)
    docs = [doc async for doc in query.stream()]
    return bool(docs)
