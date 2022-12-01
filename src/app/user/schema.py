from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    head_of_household_id: int

    class Config:
        orm_mode = True
