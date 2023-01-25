from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.auth.routers import get_authenticated_user
from .schema import RecipeSuggestion, SuggestionFilters
from database import db, views

router = APIRouter(dependencies=[Depends(get_authenticated_user)])


async def get_suggestion_filters(
    servings: Optional[float] = None,
):
    return SuggestionFilters(servings=servings)


@router.get(
    "/users/{user_id}/suggestions",
    response_model=List[RecipeSuggestion],
)
async def get_recipe_suggestions(
    user_id: int,
    db: Session = Depends(db.get_db),
    filters: SuggestionFilters = Depends(get_suggestion_filters),
):
    return views.recipe.get_suggestions(db, user_id, filters)
