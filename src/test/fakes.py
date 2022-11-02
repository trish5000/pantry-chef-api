from faker import Faker
from faker_enum import EnumProvider
from app.config import Settings
from app.food_item.schema import StorageLocation

import app.user.model as user_model
import app.food_item.model as food_item_model
import app.recipe.model as recipe_model
import app.recipe.schema as recipe_schema

fake = Faker()
fake.add_provider(EnumProvider)


def fake_settings():
    return Settings(
        token_key="fakeKey",
        oauth_android_client_id="fakeAndroidClient",
        oauth_desktop_client_id="fakeDesktopClient",
        oauth_ios_client_id="fakeIosClientId",
    )


def fake_auth_request():
    return {"token": fake.word()}


def fake_auth_response():
    user = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "id": fake.pyint(),
    }
    return {
        "access_token": fake.word(),
        "user": user,
        "new_user": fake.pybool(),
    }


def fake_db_user():
    return user_model.User(
        id=fake.pyint(max_value=50),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
    )


def fake_json_user():
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
    }


def fake_db_food_item():
    return food_item_model.FoodItem(
        name=fake.word(),
        quantity=fake.pydecimal(),
        unit=fake.word(),
        date_added=fake.date_time(),
        use_by=fake.date_time(),
        storage_location=fake.enum(StorageLocation),
        user_id=fake.pyint(max_value=50),
    )


def fake_json_food_item():
    return {
        "name": fake.word(),
        "quantity": fake.pyint(),
        "unit": fake.word(),
        "user_id": fake.pyint(max_value=50),
        "date_added": fake.date_time().strftime("%Y-%m-%dT%H:%M:%S"),
        "use_by": fake.date_time().strftime("%Y-%m-%dT%H:%M:%S"),
        "storage_location": fake.enum(StorageLocation).value,
    }


def fake_db_ingredient():
    return recipe_model.Ingredient(
        recipe_id=fake.pyint(max_value=100),
        name=fake.word(),
        quantity=fake.pydecimal(),
        unit=fake.word(),
    )


def fake_schema_ingredient():
    return recipe_schema.Ingredient(
        id=fake.pyint(max_value=500),
        recipe_id=fake.pyint(max_value=100),
        name=fake.word(),
        quantity=fake.pydecimal(),
        unit=fake.word(),
    )


def fake_db_recipe():
    return recipe_model.Recipe(
        user_id=fake.pyint(max_value=50),
        name=fake.word(),
        procedure=fake.paragraph(),
        ingredients=[fake_db_ingredient() for _ in range(fake.pyint(max_value=20))],
    )


def fake_json_ingredient():
    return {
        "name": fake.word(),
        "quantity": fake.pyfloat(),
        "unit": fake.word(),
    }


def fake_json_recipe():
    return {
        "name": fake.word(),
        "procedure": fake.paragraph(),
        "ingredients": [
            fake_json_ingredient() for _ in range(fake.pyint(max_value=20))
        ],
    }
