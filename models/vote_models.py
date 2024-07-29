from pydantic import BaseModel

from utils.enums import VoteEnum


class VoteData(BaseModel):
    cat_id: str
    vote: VoteEnum


class VoteBase(BaseModel):
    user_id: str
    cat_id: str


class VoteCreate(VoteBase):
    pass


class Vote(VoteBase):
    id: str
