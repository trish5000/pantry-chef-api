from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.food.schema import FoodItem


class IngredientBase(FoodItem):
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


class RecipeSuggestion(BaseModel):
    missing_ingredients: List[Ingredient]
    recipe: Recipe
