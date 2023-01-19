from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str
    quantity: float
    unit: str


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int

    class Config:
        orm_mode = True


class RecipeBase(BaseModel):
    name: str
    servings: float
    procedure: Optional[str]


class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]


class Recipe(RecipeBase):
    id: int
    user_id: int
    ingredients: List[Ingredient]
    timestamp: datetime

    class Config:
        orm_mode = True
