from typing import List
from fastapi import FastAPI
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.auth.routers import get_authenticated_user

from database import db
import app.household.model as household_model
import app.household.routers as household_routers
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
    household_member_one = my_fakes.fake_db_household_member(
        TOKEN_USER_ID,
        user_id=TOKEN_USER_ID,
    )
    household_member_two = my_fakes.fake_db_household_member(TOKEN_USER_ID)
    diet_prefs_one = my_fakes.fake_diet_pref(member_id=household_member_one.id)
    diet_prefs_two = my_fakes.fake_diet_pref(member_id=household_member_two.id)
    return {
        "user_one": user_one,
        "member_one": household_member_one,
        "member_two": household_member_two,
        "diet_prefs_one": diet_prefs_one,
        "diet_prefs_two": diet_prefs_two,
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
    app.include_router(household_routers.router)
    app.dependency_overrides[db.get_db] = override_get_db
    app.dependency_overrides[get_authenticated_user] = lambda: {"sub": TOKEN_USER_ID}
    yield TestClient(app)


def assertEqualDietPrefs(
    json_list: List[dict],
    db_list: List[household_model.DietaryPreferences],
):
    for i in range(len(json_list)):
        assert json_list[i]["preference"] == db_list[i].preference


def test_get_household(test_client: TestClient, global_data):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/household")
    assert response.status_code == 200

    data = response.json()
    member_one = data[0]
    global_member_one = global_data["member_one"]
    assert member_one["user_id"] == global_member_one.user_id
    assert member_one["head_of_household_id"] == global_member_one.head_of_household_id
    assertEqualDietPrefs(
        member_one["dietary_preferences"], global_member_one.dietary_preferences
    )

    member_two = data[1]
    global_member_two = global_data["member_two"]
    assert member_two["user_id"] == global_member_two.user_id
    assert member_two["head_of_household_id"] == global_member_two.head_of_household_id
    assertEqualDietPrefs(
        member_two["dietary_preferences"], global_member_two.dietary_preferences
    )


def test_add_household_member(test_client: TestClient, my_fakes: MyFakes):
    new_member = my_fakes.fake_json_household_member()

    response = test_client.post(f"/users/{TOKEN_USER_ID}/household", json=new_member)
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/household")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    returned_member = data[-1]
    assert returned_member["first_name"] == new_member["first_name"]
    assert returned_member["last_name"] == new_member["last_name"]


def test_update_household_member(test_client: TestClient):
    updated_diet_prefs = [
        {"preference": 1},
        {"preference": 2},
        {"preference": 3},
    ]

    response = test_client.get(f"/users/{TOKEN_USER_ID}/household")
    assert response.status_code == 200

    member_two = response.json()[1]
    member_two["dietary_preferences"] = updated_diet_prefs

    response = test_client.put(f"/users/{TOKEN_USER_ID}/household", json=member_two)
    assert response.status_code == 200

    updated = response.json()
    assert updated["dietary_preferences"] == updated_diet_prefs


def test_invalid_update_attempt(test_client: TestClient):
    household_response = test_client.get(f"/users/{TOKEN_USER_ID}/household")
    assert household_response.status_code == 200

    member_two = household_response.json()[1]

    # Not current user or head of household
    bad_user_id = TOKEN_USER_ID + member_two["head_of_household_id"]
    response = test_client.put(f"/users/{bad_user_id}/household", json=member_two)
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Not authorized to make changes to this household member"
    )


def test_remove_household_member(test_client: TestClient):
    response = test_client.get(f"/users/{TOKEN_USER_ID}/household")
    assert response.status_code == 200

    data = response.json()
    initial_member_count = len(data)
    member_to_delete = data[1]

    response = test_client.request(
        "DELETE",
        f"/users/{TOKEN_USER_ID}/household",
        json=member_to_delete,
    )
    assert response.status_code == 200

    response = test_client.get(f"/users/{TOKEN_USER_ID}/household")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == initial_member_count - 1
    assert not any([d["id"] == member_to_delete["id"] for d in data])


def test_invalid_delete_attempt(test_client: TestClient):
    household_response = test_client.get(f"/users/{TOKEN_USER_ID}/household")
    assert household_response.status_code == 200

    member_two = household_response.json()[1]

    # Must be head of household to delete a member
    bad_user_id = member_two["head_of_household_id"] + 1
    response = test_client.request(
        "DELETE",
        f"/users/{bad_user_id}/household",
        json=member_two,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to remove household member"

    # Can't delete yourself from household
    head_member = household_response.json()[0]
    response = test_client.request(
        "DELETE",
        f"/users/{head_member['head_of_household_id']}/household",
        json=head_member,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot remove head from own household"
