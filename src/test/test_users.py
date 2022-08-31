from faker import Faker
from fastapi import FastAPI
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from database import db
from app.user.model import User
from app.user import routers as user_routers

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
    return {
        "user_one": user_one,
        "user_two": user_two,
    }


@pytest.fixture()
def session(global_data):

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    session.add_all(
        [
            global_data["user_one"],
            global_data["user_two"],
        ]
    )
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
    app.include_router(user_routers.router)
    app.dependency_overrides[db.get_db] = override_get_db
    yield TestClient(app)


def test_get_users(test_client: TestClient, global_data):
    response = test_client.get(f"/users")
    assert response.status_code == 200

    data = response.json()

    user_one = data[0]
    assert user_one["first_name"] == global_data["user_one"].first_name
    assert user_one["last_name"] == global_data["user_one"].last_name
    assert user_one["email"] == global_data["user_one"].email

    user_two = data[1]
    assert user_two["first_name"] == global_data["user_two"].first_name
    assert user_two["last_name"] == global_data["user_two"].last_name
    assert user_two["email"] == global_data["user_two"].email


def test_add_user(test_client: TestClient):
    fake = Faker()
    new_user = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
    }

    response = test_client.post(f"/users", json=new_user)
    assert response.status_code == 200

    response = test_client.get(f"/users")
    assert response.status_code == 200

    third_user = response.json()[2]
    assert third_user["first_name"] == new_user["first_name"]
    assert third_user["last_name"] == new_user["last_name"]
    assert third_user["email"] == new_user["email"]


def test_update_user(test_client: TestClient):
    fake = Faker()
    new_first_name = fake.first_name()

    response = test_client.get(f"/users")
    assert response.status_code == 200

    user = response.json()[0]
    user["first_name"] = new_first_name

    response = test_client.put(f"/users", json=user)
    assert response.status_code == 200

    updated = response.json()
    assert updated["first_name"] == new_first_name
    assert updated["id"] == user["id"]


def test_get_user_by_id(test_client: TestClient, global_data):
    response = test_client.get(f"/users/{TOKEN_USER_ID}")
    assert response.status_code == 200

    user = response.json()
    assert user["id"] == global_data["user_one"].id
