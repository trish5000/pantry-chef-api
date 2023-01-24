from pydantic import BaseModel
from typing import List

from app.pantry.schema import PantryItem
from app.recipe.schema import Ingredient, Recipe


class RecipeSuggestion(BaseModel):
    missing_ingredients: List[Ingredient]
    pantry_items: List[PantryItem]
    recipe: Recipe
