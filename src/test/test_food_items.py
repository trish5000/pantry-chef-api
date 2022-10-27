from re import X
from faker import Faker
from faker_enum import EnumProvider
from fastapi import FastAPI
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from database import db
from app.food_item.model import FoodItem
from app.food_item.schema import StorageLocation
import app.food_item.routers as food_item_routers
from app.user.model import User

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
    fake.add_provider(EnumProvider)

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
    food_item_one = FoodItem(
        name=fake.word(),
        quantity=fake.pydecimal(),
        unit=fake.word(),
        date_added=fake.date_time(),
        use_by=fake.date_time(),
        storage_location=fake.enum(StorageLocation),
        user_id=TOKEN_USER_ID,
    )
    food_item_two = FoodItem(
        name=fake.word(),
        quantity=fake.pydecimal(),
        unit=fake.word(),
        date_added=fake.date_time(),
        use_by=fake.date_time(),
        storage_location=fake.enum(StorageLocation),
        user_id=TOKEN_USER_ID,
    )
    return {
        "user_one": user_one,
        "user_two": user_two,
        "food_item_one": food_item_one,
        "food_item_two": food_item_two,
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
    app.include_router(food_item_routers.router)
    app.dependency_overrides[db.get_db] = override_get_db
    yield TestClient(app)


def test_get_food_items(test_client: TestClient, global_data):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/food_items")
    assert response.status_code == 200

    data = response.json()

    food_item_one = data[0]
    global_item_one = global_data["food_item_one"]
    assert food_item_one["name"] == global_item_one.name
    assert food_item_one["quantity"] == global_item_one.quantity
    assert food_item_one["unit"] == global_item_one.unit
    assert food_item_one["date_added"] == global_item_one.date_added.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert food_item_one["use_by"] == global_item_one.use_by.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert food_item_one["storage_location"] == global_item_one.storage_location.value

    food_item_two = data[1]
    global_item_two = global_data["food_item_two"]
    assert food_item_two["name"] == global_item_two.name
    assert food_item_two["quantity"] == global_item_two.quantity
    assert food_item_two["unit"] == global_item_two.unit
    assert food_item_two["date_added"] == global_item_two.date_added.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert food_item_two["use_by"] == global_item_two.use_by.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    assert food_item_two["storage_location"] == global_item_two.storage_location.value


def test_add_food_item(test_client: TestClient):
    fake = Faker()
    fake.add_provider(EnumProvider)

    new_food = {
        "name": fake.word(),
        "quantity": fake.pyint(),
        "unit": fake.word(),
        "user_id": TOKEN_USER_ID,
        "date_added": fake.date_time().strftime("%Y-%m-%dT%H:%M:%S"),
        "use_by": fake.date_time().strftime("%Y-%m-%dT%H:%M:%S"),
        "storage_location": fake.enum(StorageLocation).value,
    }
    response = test_client.post(f"/users/{TOKEN_USER_ID}/food_items", json=new_food)
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/food_items")
    assert response.status_code == 200

    data = response.json()

    food_item_three = data[2]
    assert food_item_three["name"] == new_food["name"]
    assert food_item_three["quantity"] == new_food["quantity"]
    assert food_item_three["unit"] == new_food["unit"]
    assert food_item_three["date_added"] == new_food["date_added"]
    assert food_item_three["use_by"] == new_food["use_by"]
    assert food_item_three["storage_location"] == new_food["storage_location"]


def test_update_food_item(test_client: TestClient):
    fake = Faker()
    updated_food_name = fake.word()

    response = test_client.get(f"/users/{TOKEN_USER_ID}/food_items")
    assert response.status_code == 200

    food_item_one = response.json()[0]
    food_item_one["name"] = updated_food_name

    response = test_client.put(f"/users/{TOKEN_USER_ID}/food_items", json=food_item_one)
    assert response.status_code == 200

    updated = response.json()
    assert updated["name"] == updated_food_name
    assert updated["id"] == food_item_one["id"]


def test_delete_food_item(test_client: TestClient):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/food_items")
    assert response.status_code == 200

    data = response.json()
    initial_food_count = len(data)
    item_to_delete = data[1]

    response = test_client.delete(
        f"/users/{TOKEN_USER_ID}/food_items", json=item_to_delete
    )
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/food_items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == initial_food_count - 1
    assert not any([d["name"] == item_to_delete["name"] for d in data])
