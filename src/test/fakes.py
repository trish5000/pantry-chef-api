from faker import Faker
from faker_enum import EnumProvider
from app.config import Settings
from app.food_item.schema import StorageLocation

import app.user.model as user_model
import app.food_item.model as food_item_model
import app.recipe.model as recipe_model
import app.recipe.schema as recipe_schema
import app.household.model as household_model
import app.household.schema as household_schema

fake = Faker()
fake.add_provider(EnumProvider)


class MyFakes:
    def __init__(self):
        self.user_id = 2

    def fake_settings(self):
        return Settings(
            token_key="fakeKey",
            oauth_android_client_id="fakeAndroidClient",
            oauth_desktop_client_id="fakeDesktopClient",
            oauth_ios_client_id="fakeIosClientId",
        )

    def fake_auth_request(self):
        return {"token": fake.word()}

    def fake_auth_response(self):
        self.user_id += 1

        user = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "id": self.user_id,
        }
        return {
            "access_token": fake.word(),
            "user": user,
            "new_user": fake.pybool(),
        }

    def fake_db_user(self):
        self.user_id += 1

        return user_model.User(
            id=self.user_id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
        )

    def fake_json_user(self):
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
        }

    def fake_db_household_member(
        self,
        head_of_household_id: int,
        user_id: int = None,
    ):
        return household_model.HouseholdMember(
            user_id=user_id,
            first_name=fake.first_name(),
            head_of_household_id=head_of_household_id,
        )

    def fake_json_household_member(self):
        return {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "child": fake.pybool(),
        }

    def fake_diet_pref(self, member_id: int):
        return household_model.DietaryPreferences(
            member_id=member_id,
            preference=fake.enum(household_schema.DietaryPreferenceEnum),
        )

    def fake_db_food_item(self):
        self.user_id += 1

        return food_item_model.FoodItem(
            name=fake.word(),
            quantity=fake.pydecimal(),
            unit=fake.word(),
            date_added=fake.date_time(),
            use_by=fake.date_time(),
            storage_location=fake.enum(StorageLocation),
            user_id=self.user_id,
        )

    def fake_json_food_item(self):
        self.user_id += 1

        return {
            "name": fake.word(),
            "quantity": fake.pyint(),
            "unit": fake.word(),
            "user_id": self.user_id,
            "date_added": fake.date_time().strftime("%Y-%m-%dT%H:%M:%S"),
            "use_by": fake.date_time().strftime("%Y-%m-%dT%H:%M:%S"),
            "storage_location": fake.enum(StorageLocation).value,
        }

    def fake_db_ingredient(self):
        return recipe_model.Ingredient(
            recipe_id=fake.pyint(max_value=100),
            name=fake.word(),
            quantity=fake.pydecimal(),
            unit=fake.word(),
        )

    def fake_schema_ingredient(self):
        return recipe_schema.Ingredient(
            id=fake.pyint(max_value=500),
            recipe_id=fake.pyint(max_value=100),
            name=fake.word(),
            quantity=fake.pydecimal(),
            unit=fake.word(),
        )

    def fake_db_recipe(self):
        self.user_id += 1

        return recipe_model.Recipe(
            user_id=self.user_id,
            name=fake.word(),
            procedure=fake.paragraph(),
            servings=fake.pyfloat(),
            ingredients=[
                self.fake_db_ingredient() for _ in range(fake.pyint(max_value=20))
            ],
        )

    def fake_json_ingredient(self):
        return {
            "name": fake.word(),
            "quantity": fake.pyfloat(),
            "unit": fake.word(),
        }

    def fake_json_recipe(self):
        return {
            "name": fake.word(),
            "procedure": fake.paragraph(),
            "ingredients": [
                self.fake_json_ingredient() for _ in range(fake.pyint(max_value=20))
            ],
            "servings": fake.pyfloat(),
        }
