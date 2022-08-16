from fastapi import FastAPI

from app.food_item.routers import router as food_item_router
from app.user.routers import router as user_router
from app.user.schema import UserCreate
from database import crud, db

db.Base.metadata.create_all(bind=db.engine)


def seed_test_data():
    session = db.SessionLocal()
    existing = crud.user.get_all(session)
    if len(existing) > 0:
        return

    marlow = UserCreate(
        first_name="Marlow",
        last_name="Stanfield",
        email="marlow.stanfield@gmail.com",
    )
    crud.user.create(session, marlow)

    hannah = UserCreate(
        first_name="Hannah",
        last_name="Horvath",
        email="writerGrl@hotmail.com",
    )
    crud.user.create(session, hannah)


app = FastAPI()

seed_test_data()

app.include_router(user_router)
app.include_router(food_item_router)
