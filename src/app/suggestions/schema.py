from pydantic import BaseModel
from typing import List, Optional

from app.pantry.schema import PantryItem
from app.recipe.schema import Ingredient, Recipe


class RecipeSuggestion(BaseModel):
    missing_ingredients: List[Ingredient]
    pantry_items: List[PantryItem]
    recipe: Recipe


class SuggestionFilters(BaseModel):
    servings: Optional[float]
