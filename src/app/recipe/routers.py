from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .schema import Recipe, RecipeCreate
from database import crud, db

router = APIRouter()


@router.post("/users/{user_id}/recipes", response_model=Recipe)
async def add_recipe(
    user_id: int,
    recipe: RecipeCreate,
    db: Session = Depends(db.get_db),
):
    return crud.recipe.add(db, user_id, recipe)


@router.get("/users/{user_id}/recipes", response_model=List[Recipe])
async def get_recipes(
    user_id: int,
    db: Session = Depends(db.get_db),
):
    return crud.recipe.get_all(db, user_id)


@router.put("/users/{user_id}/recipes", response_model=Recipe)
async def update_recipe(
    user_id: int,
    recipe: Recipe,
    db: Session = Depends(db.get_db),
):
    return crud.recipe.update(db, user_id, recipe)


@router.delete("/users/{user_id}/recipes")
async def delete_recipe(
    user_id: int,
    recipe: Recipe,
    db: Session = Depends(db.get_db),
):
    crud.recipe.delete(db, user_id, recipe)
