from datetime import datetime
from pydantic import BaseModel


class FoodItemBase(BaseModel):
    name: str
    quantity: float
    unit: str


class FoodItemCreate(FoodItemBase):
    pass


class FoodItem(FoodItemCreate):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
