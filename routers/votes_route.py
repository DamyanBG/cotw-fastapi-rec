from fastapi import APIRouter, Depends

from models.vote_models import Vote, VoteCreate, VoteData
from models.user_models import UserId
from auth.token import get_current_user_id
from queries.vote_queries import insert_vote
from queries.cat_queries import add_dislike, add_like
from utils.enums import VoteEnum


votes_router = APIRouter(prefix="/vote", tags=["vote"])


@votes_router.post("/", response_model=Vote)
async def post_vote(vote_data: VoteData, user_id: UserId = Depends(get_current_user_id)):
    vote_create_data = VoteCreate(user_id=user_id.id, cat_id=vote_data.cat_id)
    vote = await insert_vote(vote_create_data)

    if vote_data.vote == VoteEnum.Like:
        await add_like(vote.cat_id)
    else:
        await add_dislike(vote.cat_id)

    return vote
