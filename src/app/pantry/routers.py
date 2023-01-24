from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.auth.routers import get_authenticated_user
from .schema import PantryItem, PantryItemCreate
from database import crud, db

router = APIRouter(dependencies=[Depends(get_authenticated_user)])


@router.post("/users/{user_id}/pantry_items", response_model=PantryItem)
async def add_pantry_item(
    user_id: int,
    pantry_item: PantryItemCreate,
    db: Session = Depends(db.get_db),
):
    return crud.pantry.add(db, user_id, pantry_item)


@router.get("/users/{user_id}/pantry_items", response_model=List[PantryItem])
async def get_pantry_items(
    user_id: int,
    db: Session = Depends(db.get_db),
):
    return crud.pantry.get_all(db, user_id)


@router.put("/users/{user_id}/pantry_items", response_model=PantryItem)
async def update_pantry_item(
    user_id: int,
    pantry_item: PantryItem,
    db: Session = Depends(db.get_db),
):
    return crud.pantry.update(db, user_id, pantry_item)


@router.delete("/users/{user_id}/pantry_items")
async def delete_pantry_item(
    user_id: int,
    pantry_item: PantryItem,
    db: Session = Depends(db.get_db),
):
    crud.pantry.delete(db, user_id, pantry_item)
