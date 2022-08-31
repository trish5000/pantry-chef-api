from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .schema import User, UserCreate
from database import crud, db
from typing import List

router = APIRouter()


@router.post("/users", response_model=User)
async def add_user(user: UserCreate, session: Session = Depends(db.get_db)):
    return crud.user.create(session, user)


@router.get("/users", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(db.get_db)):
    return crud.user.get_all(db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=User)
async def read_user_by_id(user_id: int, session: Session = Depends(db.get_db)):
    return crud.user.get(session, user_id)


@router.put("/users", response_model=User)
async def update_user(user: User, session: Session = Depends(db.get_db)):
    return crud.user.update(session, user)
