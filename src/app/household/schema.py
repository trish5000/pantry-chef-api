from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

# TODO make child an ageGroup enum


class DietaryPreferenceEnum(Enum):
    VEGETARIAN = 0
    PESCATARIAN = 1
    VEGAN = 2
    GLUTEN_FREE = 3


class DietaryPreferenceBase(BaseModel):
    pass


class DietaryPreferenceCreate(DietaryPreferenceBase):
    preference: Optional[DietaryPreferenceEnum]


class DietaryPreference(DietaryPreferenceBase):
    preference: DietaryPreferenceEnum

    class Config:
        orm_mode = True


class HouseholdMemberBase(BaseModel):
    last_name: Optional[str]
    user_id: Optional[int]


class HouseholdMemberCreate(HouseholdMemberBase):
    first_name: Optional[str]
    dietary_preferences: Optional[List[DietaryPreferenceCreate]]
    child: Optional[bool]


class HouseholdMember(HouseholdMemberBase):
    id: int
    head_of_household_id: int
    first_name: str
    child: bool
    dietary_preferences: List[DietaryPreference]

    class Config:
        orm_mode = True
