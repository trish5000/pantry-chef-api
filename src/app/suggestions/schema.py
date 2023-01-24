from pydantic import BaseModel
from typing import List

from app.recipe.schema import Ingredient, Recipe


class RecipeSuggestion(BaseModel):
    missing_ingredients: List[Ingredient]
    recipe: Recipe
