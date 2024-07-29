from enum import Enum


class VoteEnum(str, Enum):
    Like = "like"
    Dislike = "dislike"
    Pass = "pass"
