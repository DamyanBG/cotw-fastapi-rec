from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    token: str


class Credentials(BaseModel):
    password: str
    email: EmailStr
