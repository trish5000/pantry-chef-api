from decimal import Decimal
import json
from typing import List
from faker import Faker
from fastapi import FastAPI
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from database import db
from app.user.model import User
import app.recipe.model as recipe_model
import app.recipe.routers as recipe_routers


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def assertEqualIngredients(
    json_list: List[dict], db_list: List[recipe_model.Ingredient]
):
    for i in range(len(json_list)):
        assert json_list[i]["name"] == db_list[i].name
        assert json_list[i]["quantity"] == db_list[i].quantity
        assert json_list[i]["unit"] == db_list[i].unit


TOKEN_USER_ID = 1
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = sa.create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db.Base.metadata.drop_all(bind=engine)
db.Base.metadata.create_all(bind=engine)


@pytest.fixture()
def global_data():
    fake = Faker()

    user_one = User(
        id=TOKEN_USER_ID,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
    )
    user_two = User(
        id=2,
        first_name="tammy",
        last_name="one",
        email=fake.email(),
    )

    ingredient_one = recipe_model.Ingredient(
        recipe_id=1,
        name=fake.word(),
        quantity=fake.pydecimal(),
        unit=fake.word(),
    )

    ingredient_two = recipe_model.Ingredient(
        recipe_id=1,
        name=fake.word(),
        quantity=fake.pydecimal(),
        unit=fake.word(),
    )

    recipe_one = recipe_model.Recipe(
        user_id=TOKEN_USER_ID,
        name=fake.word(),
        procedure=fake.paragraph(),
        ingredients=[ingredient_one, ingredient_two],
    )

    return {
        "user_one": user_one,
        "user_two": user_two,
        "recipe_one": recipe_one,
    }


@pytest.fixture()
def session(global_data):

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    session.add_all([v for _, v in global_data.items()])
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def test_client(session):
    def override_get_db():
        yield session

    app = FastAPI()
    app.include_router(recipe_routers.router)
    app.dependency_overrides[db.get_db] = override_get_db
    yield TestClient(app)


def test_get_recipe(test_client: TestClient, global_data):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/recipes")
    assert response.status_code == 200

    data = response.json()

    recipe_one = data[0]
    global_recipe_one = global_data["recipe_one"]
    assert recipe_one["name"] == global_recipe_one.name
    assert recipe_one["procedure"] == global_recipe_one.procedure
    assertEqualIngredients(recipe_one["ingredients"], global_recipe_one.ingredients)


def test_add_recipe(test_client: TestClient):
    def assertSameIngredients(new_ingredients, returned_ingredients):
        assert len(new_ingredients) == len(returned_ingredients)

        for ingredient in returned_ingredients:
            ingredient.pop("id")

        for i in range(len(new_ingredients)):
            assert new_ingredients[i] in returned_ingredients

    fake = Faker()

    def fake_ingredient():
        return {
            "name": fake.word(),
            "quantity": fake.pyfloat(),
            "unit": fake.word(),
        }

    new_recipe = {
        "name": fake.word(),
        "procedure": fake.paragraph(),
        "ingredients": [fake_ingredient() for _ in range(fake.pyint(max_value=20))],
    }

    response = test_client.post(f"/users/{TOKEN_USER_ID}/recipes", json=new_recipe)
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/recipes")
    assert response.status_code == 200

    returned_recipe = response.json()[1]
    assert returned_recipe["name"] == new_recipe["name"]
    assert returned_recipe["procedure"] == new_recipe["procedure"]
    assertSameIngredients(
        new_recipe["ingredients"],
        returned_recipe["ingredients"],
    )


def test_update_recipe(test_client: TestClient):
    fake = Faker()
    updated_recipe_name = fake.word()

    response = test_client.get(f"/users/{TOKEN_USER_ID}/recipes")
    assert response.status_code == 200

    recipe_one = response.json()[0]
    recipe_one["name"] = updated_recipe_name

    response = test_client.put(f"/users/{TOKEN_USER_ID}/recipes", json=recipe_one)
    assert response.status_code == 200

    updated = response.json()
    assert updated["name"] == updated_recipe_name
    assert updated["id"] == recipe_one["id"]


def test_delete_recipe(test_client: TestClient):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/recipes")
    assert response.status_code == 200

    data = response.json()
    initial_recipe_count = len(data)
    item_to_delete = data[0]

    response = test_client.delete(
        f"/users/{TOKEN_USER_ID}/recipes", json=item_to_delete
    )
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/recipes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == initial_recipe_count - 1
    assert not any([d["name"] == item_to_delete["name"] for d in data])
