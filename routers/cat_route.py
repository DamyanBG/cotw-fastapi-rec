from typing import Union
from fastapi import APIRouter, status, Depends, HTTPException
from google.cloud.exceptions import NotFound

from auth.token import get_current_user_id
from models.cat_models import NextRoundCat, NextRoundCatData, NextRoundCatCreate, NextRoundCatWithImage, CurrentRoundCatWithImage
from models.user_models import UserId
from queries.cat_queries import insert_nrc, select_user_nrc, select_not_voted_cat
from queries.image_queries import select_image_file_name_by_id
from queries.vote_queries import select_voted_cats_ids
from storage.google_cloud_storage import generate_signed_url


cats_router = APIRouter(prefix="/cats", tags=["cats"])


@cats_router.post("/create", response_model=NextRoundCat, status_code=status.HTTP_201_CREATED)
async def post_cat(cat_data: NextRoundCatData, user_id: UserId = Depends(get_current_user_id)):
    existing_cat = await select_user_nrc(user_id.id)
    if existing_cat:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already uploaded a cat for the next round!")

    cat_create_data = NextRoundCatCreate(user_id=user_id.id, **cat_data.model_dump())
    next_round_cat = await insert_nrc(cat_create_data)
    return next_round_cat


@cats_router.get("/user-cat", response_model=NextRoundCatWithImage)
async def get_user_nrc(user_id: UserId = Depends(get_current_user_id)):
    user_nrc = await select_user_nrc(user_id.id)
    if not user_nrc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You do not uploaded a cat for the next round!")
    
    nrc_image_file_name = await select_image_file_name_by_id(user_nrc.photo_id)
    nrc_image_url = generate_signed_url(nrc_image_file_name)
    user_ncr_with_image = NextRoundCatWithImage(
        image_url=nrc_image_url, **user_nrc.model_dump()
    )
    return user_ncr_with_image


@cats_router.get("/cat-for-vote", response_model=Union[CurrentRoundCatWithImage, dict[str, str]])
async def get_cat_for_vote(user_id: UserId = Depends(get_current_user_id)):
    user_voted_cats_ids = await select_voted_cats_ids(user_id.id)
    try:
        cat_for_vote = await select_not_voted_cat(user_voted_cats_ids)
    except NotFound:
        return {"message": "No cat for vote!"}
    
    cat_image_file_name = await select_image_file_name_by_id(cat_for_vote.photo_id)
    cat_image_url = generate_signed_url(cat_image_file_name)
    cat_for_vote_with_image = CurrentRoundCatWithImage(
        image_url=cat_image_url, **cat_for_vote.model_dump()
    )

    return cat_for_vote_with_image
