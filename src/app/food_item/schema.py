from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class StorageLocation(Enum):
    FRIDGE = 0
    FREEZER = 1
    PANTRY = 2
    SPICE_RACK = 3


class FoodItemBase(BaseModel):
    name: str
    quantity: float
    unit: str
    storage_location: StorageLocation
    date_added: datetime
    use_by: datetime


class FoodItemCreate(FoodItemBase):
    pass


class FoodItem(FoodItemBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
