from faker import Faker
from faker_enum import EnumProvider
from fastapi import FastAPI
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from database import db
from app.auth.routers import get_authenticated_user
import app.pantry.routers as pantry_routers
from test.fakes import MyFakes

TOKEN_USER_ID = 1
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = sa.create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db.Base.metadata.drop_all(bind=engine)
db.Base.metadata.create_all(bind=engine)


@pytest.fixture
def my_fakes():
    return MyFakes()


@pytest.fixture()
def global_data(my_fakes: MyFakes):
    user_one = my_fakes.fake_db_user()
    user_one.id = TOKEN_USER_ID

    user_two = my_fakes.fake_db_user()

    pantry_item_one = my_fakes.fake_db_pantry_item()
    pantry_item_one.user_id = TOKEN_USER_ID

    pantry_item_two = my_fakes.fake_db_pantry_item()
    pantry_item_two.user_id = TOKEN_USER_ID

    return {
        "user_one": user_one,
        "user_two": user_two,
        "pantry_item_one": pantry_item_one,
        "pantry_item_two": pantry_item_two,
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
    app.include_router(pantry_routers.router)
    app.dependency_overrides[db.get_db] = override_get_db
    app.dependency_overrides[get_authenticated_user] = lambda: {"sub": TOKEN_USER_ID}
    yield TestClient(app)


def test_get_pantry_items(test_client: TestClient, global_data):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/pantry_items")
    assert response.status_code == 200

    data = response.json()

    pantry_item_one = data[0]
    global_item_one = global_data["pantry_item_one"]
    assert pantry_item_one["name"] == global_item_one.name
    assert pantry_item_one["quantity"] == global_item_one.quantity
    assert pantry_item_one["unit"] == global_item_one.unit
    assert pantry_item_one["date_added"] == global_item_one.date_added.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert pantry_item_one["use_by"] == global_item_one.use_by.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert pantry_item_one["storage_location"] == global_item_one.storage_location.value

    pantry_item_two = data[1]
    global_item_two = global_data["pantry_item_two"]
    assert pantry_item_two["name"] == global_item_two.name
    assert pantry_item_two["quantity"] == global_item_two.quantity
    assert pantry_item_two["unit"] == global_item_two.unit
    assert pantry_item_two["date_added"] == global_item_two.date_added.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert pantry_item_two["use_by"] == global_item_two.use_by.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert pantry_item_two["storage_location"] == global_item_two.storage_location.value


def test_add_pantry_item(test_client: TestClient, my_fakes: MyFakes):
    fake = Faker()
    fake.add_provider(EnumProvider)

    new_food = my_fakes.fake_json_pantry_item()
    new_food["user_id"] = TOKEN_USER_ID

    response = test_client.post(f"/users/{TOKEN_USER_ID}/pantry_items", json=new_food)
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/pantry_items")
    assert response.status_code == 200

    data = response.json()

    pantry_item_three = data[2]
    assert pantry_item_three["name"] == new_food["name"]
    assert pantry_item_three["quantity"] == new_food["quantity"]
    assert pantry_item_three["unit"] == new_food["unit"]
    assert pantry_item_three["date_added"] == new_food["date_added"]
    assert pantry_item_three["use_by"] == new_food["use_by"]
    assert pantry_item_three["storage_location"] == new_food["storage_location"]


def test_update_pantry_item(test_client: TestClient):
    fake = Faker()
    updated_food_name = fake.word()

    response = test_client.get(f"/users/{TOKEN_USER_ID}/pantry_items")
    assert response.status_code == 200

    pantry_item_one = response.json()[0]
    pantry_item_one["name"] = updated_food_name

    response = test_client.put(
        f"/users/{TOKEN_USER_ID}/pantry_items", json=pantry_item_one
    )
    assert response.status_code == 200

    updated = response.json()
    assert updated["name"] == updated_food_name
    assert updated["id"] == pantry_item_one["id"]


def test_delete_pantry_item(test_client: TestClient):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/pantry_items")
    assert response.status_code == 200

    data = response.json()
    initial_food_count = len(data)
    item_to_delete = data[1]

    response = test_client.request(
        "DELETE",
        f"/users/{TOKEN_USER_ID}/pantry_items",
        json=item_to_delete,
    )
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/pantry_items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == initial_food_count - 1
    assert not any([d["name"] == item_to_delete["name"] for d in data])
