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
