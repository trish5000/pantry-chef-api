from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.auth.routers import get_authenticated_user
from .schema import RecipeSuggestion
from database import db, views

router = APIRouter(dependencies=[Depends(get_authenticated_user)])


@router.get(
    "/users/{user_id}/suggestions",
    response_model=List[RecipeSuggestion],
)
async def get_recipe_suggestions(
    user_id: int,
    db: Session = Depends(db.get_db),
):
    return views.recipe.get_suggestions(db, user_id)
