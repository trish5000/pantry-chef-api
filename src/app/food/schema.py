from pydantic import BaseModel


class FoodItem(BaseModel):
    name: str
