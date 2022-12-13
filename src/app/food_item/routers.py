from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.auth.routers import get_authenticated_user
from .schema import FoodItem, FoodItemCreate
from database import crud, db

router = APIRouter(dependencies=[Depends(get_authenticated_user)])


@router.post("/users/{user_id}/food_items", response_model=FoodItem)
async def add_food_item(
    user_id: int,
    food_item: FoodItemCreate,
    db: Session = Depends(db.get_db),
):
    return crud.food_item.add(db, user_id, food_item)


@router.get("/users/{user_id}/food_items", response_model=List[FoodItem])
async def get_food_items(
    user_id: int,
    db: Session = Depends(db.get_db),
):
    return crud.food_item.get_all(db, user_id)


@router.put("/users/{user_id}/food_items", response_model=FoodItem)
async def update_food_item(
    user_id: int,
    food_item: FoodItem,
    db: Session = Depends(db.get_db),
):
    return crud.food_item.update(db, user_id, food_item)


@router.delete("/users/{user_id}/food_items")
async def delete_food_item(
    user_id: int,
    food_item: FoodItem,
    db: Session = Depends(db.get_db),
):
    crud.food_item.delete(db, user_id, food_item)
