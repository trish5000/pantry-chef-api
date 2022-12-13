from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.auth.routers import get_authenticated_user
from .schema import HouseholdMemberCreate, HouseholdMember
from database import crud, db

router = APIRouter(dependencies=[Depends(get_authenticated_user)])


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
    if (
        user_id != household_member.user_id
        and user_id != household_member.head_of_household_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to make changes to this household member",
        )
    return crud.household.update(db, household_member)


@router.delete("/users/{user_id}/household")
async def remove_household_member(
    user_id: int,
    household_member: HouseholdMember,
    db: Session = Depends(db.get_db),
):
    if user_id != household_member.head_of_household_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to remove household member",
        )

    if household_member.user_id == household_member.head_of_household_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot remove head from own household",
        )

    crud.household.remove_from_household(db, household_member)
