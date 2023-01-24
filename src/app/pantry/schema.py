from datetime import datetime
from enum import Enum

from app.food.schema import FoodItem


class StorageLocation(Enum):
    FRIDGE = 0
    FREEZER = 1
    PANTRY = 2
    SPICE_RACK = 3


class PantryItemBase(FoodItem):
    quantity: float
    unit: str
    storage_location: StorageLocation
    date_added: datetime
    use_by: datetime


class PantryItemCreate(PantryItemBase):
    pass


class PantryItem(PantryItemBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
