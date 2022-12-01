from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .schema import HouseholdMemberCreate, HouseholdMember
from database import crud, db

router = APIRouter()

# TODO add authentication dependency


@router.post("/users/{user_id}/household", response_model=HouseholdMember)
async def add_household_member(
    user_id: int,
    household_member: HouseholdMemberCreate,
    db: Session = Depends(db.get_db),
):
    return crud.household.add_member(db, user_id, household_member)


@router.get("/users/{user_id}/household", response_model=List[HouseholdMember])
async def get_household_members(
    user_id: int,
    db: Session = Depends(db.get_db),
):
    return crud.household.get_all(db, user_id)


@router.put("/users/{user_id}/household", response_model=HouseholdMember)
async def update_household_member(
    user_id: int,
    household_member: HouseholdMember,
    db: Session = Depends(db.get_db),
):
    # TODO throw error if user_id is not the new head of household?
    # Confused about who requests change of household...
    return crud.household.update(db, household_member)


@router.delete("/users/{user_id}/household")
async def delete_household_member(
    user_id: int,
    household_member: HouseholdMember,
    db: Session = Depends(db.get_db),
):
    crud.household.delete(db, user_id, household_member)
