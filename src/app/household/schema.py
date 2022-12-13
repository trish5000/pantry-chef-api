from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

# TODO make child an ageGroup enum


class DietaryPreferences(Enum):
    NONE = 0
    VEGETARIAN = 1
    PESCATARIAN = 2
    VEGAN = 3
    GLUTEN_FREE = 4


class HouseholdMemberBase(BaseModel):
    last_name: Optional[str]
    user_id: Optional[int]


class HouseholdMemberCreate(HouseholdMemberBase):
    first_name: Optional[str]
    dietary_preferences: Optional[List[DietaryPreferences]]
    child: Optional[bool]


class HouseholdMember(HouseholdMemberBase):
    id: int
    head_of_household_id: int
    first_name: str
    child: bool
    dietary_preferences: List[DietaryPreferences]

    class Config:
        orm_mode = True


class Profile(BaseModel):
    id: int
    user_id: int
    household_members: List[HouseholdMember]
    timestamp: datetime

    class Config:
        orm_mode = True
