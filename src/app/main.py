from fastapi import FastAPI

from app.auth.routers import router as auth_router
from app.pantry.routers import router as pantry_router
from app.household.routers import router as household_router
from app.recipe.routers import router as recipe_router
from app.recipe.schema import IngredientCreate, RecipeCreate
from app.user.routers import router as user_router
from app.user.schema import UserCreate
from database import crud, db

db.Base.metadata.create_all(bind=db.engine)


def seed_test_data():
    session = db.SessionLocal()
    existing = crud.user.get_all(session)
    if len(existing) > 0:
        return

    michelle = UserCreate(
        first_name="Michelle",
        last_name="Tolfa",
        email="michelle.tolfa@gmail.com",
    )
    db_michelle = crud.user.create(session, michelle)

    alex = UserCreate(
        first_name="Alex",
        last_name="Cahoon",
        email="cahoon.alex@gmail.com",
    )
    crud.user.create(session, alex)

    hannah = UserCreate(
        first_name="Hannah",
        last_name="Horvath",
        email="writerGrl@hotmail.com",
    )
    crud.user.create(session, hannah)

    milk = IngredientCreate(name="milk", quantity=1, unit="liter")
    froot_loops = IngredientCreate(name="froot loops", quantity=2, unit="cups")
    cereal = RecipeCreate(
        name="cereal",
        procedure="pour the milk",
        ingredients=[milk, froot_loops],
        servings=4,
    )
    crud.recipe.add(session, db_michelle.id, cereal)


app = FastAPI()

seed_test_data()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(pantry_router)
app.include_router(recipe_router)
app.include_router(household_router)
