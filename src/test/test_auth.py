from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
import jwt
import pytest

from app.auth import routers as auth_routers
from app.config import get_settings
from database import auth, db
from test.fakes import MyFakes


@pytest.fixture
def my_fakes():
    return MyFakes()


@pytest.fixture
def test_app(my_fakes: MyFakes):
    app = FastAPI()
    app.include_router(auth_routers.router)
    app.dependency_overrides[get_settings] = my_fakes.fake_settings
    app.dependency_overrides[db.get_db] = lambda: None
    yield TestClient(app)


@pytest.fixture
def fake():
    return Faker()


def test_authenticate(test_app, monkeypatch, my_fakes: MyFakes):
    fake_response = my_fakes.fake_auth_response()

    def mock_authenticate(*args, **kwargs):
        return fake_response

    monkeypatch.setattr(auth.auth, "authenticate", mock_authenticate)

    response = test_app.post("/auth/authenticate", json=my_fakes.fake_auth_request())
    assert response.status_code == 200
    assert response.json() == fake_response


def test_create_access_token(fake, my_fakes: MyFakes):
    user_id = fake.pyint()
    access_token_data: dict = {
        "sub": user_id,
        "user_id": user_id,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    settings = my_fakes.fake_settings()
    encoded_jwt = jwt.encode(access_token_data, settings.token_key)

    token = auth.auth.create_access_token(access_token_data, settings)
    assert token == encoded_jwt
