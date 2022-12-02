from fastapi import HTTPException
from sqlalchemy.orm import Session

import app.food_item.model as food_item_model
import app.food_item.schema as food_item_schema
import app.recipe.model as recipe_model
import app.recipe.schema as recipe_schema
import app.user.model as user_model
import app.user.schema as user_schema
import app.household.schema as household_schema
import app.household.model as household_model


class user:
    @staticmethod
    def get(db: Session, id: int):
        db_user = db.query(user_model.User).filter(user_model.User.id == id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(user_model.User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user: user_schema.UserCreate):
        db_user = user_model.User(**user.dict())

        db.add(db_user)
        db.commit()
        db_user.head_of_household_id = db_user.id

        db.commit()
        db.refresh(db_user)

        household.add_member(
            db,
            db_user.id,
            household_schema.HouseholdMemberCreate(user_id=db_user.id),
        )
        return db_user

    @staticmethod
    def update(db: Session, updated_user: user_schema.User):
        db_user: user_model.User = user.get(db, updated_user.id)
        db_user.first_name = updated_user.first_name
        db_user.last_name = updated_user.last_name
        db_user.head_of_household_id = updated_user.head_of_household_id
        db.commit()
        db.refresh(db_user)
        return db_user


class household:
    @staticmethod
    def add_member(
        db: Session,
        user_id: int,
        member: household_schema.HouseholdMemberCreate,
    ):
        diet_prefs = (
            [] if member.dietary_preferences is None else member.dietary_preferences
        )
        db_user = user.get(db, user_id)

        db_member = household_model.HouseholdMember(
            head_of_household_id=db_user.head_of_household_id,
            first_name=member.first_name,
            last_name=member.last_name,
            dietary_preferences=diet_prefs,
            user_id=member.user_id,
            child=member.child,
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def get_all(db: Session, user_id: int):
        db_user = user.get(db, user_id)
        db_users = db.query(user_model.User).filter(
            user_model.User.head_of_household_id == db_user.head_of_household_id
        )
        db_members = (
            db.query(household_model.HouseholdMember)
            .filter(
                household_model.HouseholdMember.head_of_household_id
                == db_user.head_of_household_id
            )
            .all()
        )
        for member in db_members:
            if member.user_id is not None:
                u: user_model.User = db_users.filter(
                    user_model.User.id == member.user_id
                ).first()
                member.first_name = u.first_name
                member.last_name = u.last_name
        return db_members

    @staticmethod
    def update(db: Session, member: household_schema.HouseholdMember):
        db_member: household_model.HouseholdMember = (
            db.query(household_model.HouseholdMember)
            .filter(
                household_model.HouseholdMember.id == member.id,
            )
            .first()
        )

        # If head of household changed, update in user table first
        if (
            db_member.user_id is not None
            and member.head_of_household_id != db_member.head_of_household_id
        ):
            db_user = user.get(db, db_member.user_id)
            user.update(
                db,
                user_schema.User(
                    id=db_user.id,
                    first_name=db_user.first_name,
                    last_name=db_user.last_name,
                    email=db_user.email,
                    head_of_household_id=member.head_of_household_id,
                ),
            )
            # user_schema.User(**db_user.dict()) probably can't do this

        db_member.first_name = member.first_name
        db_member.last_name = member.last_name
        db_member.child = member.child
        db_member.dietary_preferences = member.dietary_preferences
        db_member.head_of_household_id = member.head_of_household_id
        db_member.user_id = member.user_id

        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def delete(db: Session, member: household_schema.HouseholdMember):
        # TODO eventually - deleting a member or user will mess up people
        # who had that person as head of household.
        # need to have it automatically switch them back to themselves
        db.query(household_model.HouseholdMember).filter(
            household_model.HouseholdMember.id == member.id,
        ).delete()
        db.commit()


class food_item:
    @staticmethod
    def add(db: Session, user_id: int, food_item: food_item_schema.FoodItemCreate):
        db_food_item = food_item_model.FoodItem(**food_item.dict())
        db_food_item.user_id = user_id
        db.add(db_food_item)
        db.commit()
        db.refresh(db_food_item)
        return db_food_item

    @staticmethod
    def get_all(db: Session, user_id: int):
        return (
            db.query(food_item_model.FoodItem)
            .filter(food_item_model.FoodItem.user_id == user_id)
            .all()
        )

    @staticmethod
    def update(db: Session, user_id: int, item: food_item_schema.FoodItem):
        db_food_item = (
            db.query(food_item_model.FoodItem)
            .filter(
                food_item_model.FoodItem.user_id == user_id,
                food_item_model.FoodItem.id == item.id,
            )
            .first()
        )
        db_food_item.name = item.name
        db_food_item.quantity = item.quantity
        db_food_item.unit = item.unit
        db_food_item.storage_location = item.storage_location
        db_food_item.date_added = item.date_added
        db_food_item.use_by = item.use_by

        db.commit()
        db.refresh(db_food_item)
        return db_food_item

    @staticmethod
    def delete(db: Session, user_id: int, item: food_item_schema.FoodItem):
        db.query(food_item_model.FoodItem).filter(
            food_item_model.FoodItem.user_id == user_id,
            food_item_model.FoodItem.name == item.name,
        ).delete()
        db.commit()


class recipe:
    @staticmethod
    def add(db: Session, user_id: int, recipe: recipe_schema.RecipeCreate):
        db_ingredients = [
            recipe_model.Ingredient(**e.dict()) for e in recipe.ingredients
        ]
        db_recipe = recipe_model.Recipe(
            user_id=user_id,
            name=recipe.name,
            ingredients=db_ingredients,
            procedure=recipe.procedure,
        )
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)
        return db_recipe

    @staticmethod
    def get_all(db: Session, user_id: int):
        return (
            db.query(recipe_model.Recipe)
            .filter(recipe_model.Recipe.user_id == user_id)
            .all()
        )

    @staticmethod
    def update(db: Session, user_id: int, recipe: recipe_schema.Recipe):
        db.query(recipe_model.Ingredient).filter(
            recipe_model.Ingredient.recipe_id == recipe.id
        ).delete()  # TODO check if this works

        db_ingredients = [
            recipe_model.Ingredient(**e.dict()) for e in recipe.ingredients
        ]

        # TODO? Do i need to filter by user ID AND recipe ID?
        # aren't all recipe ids unique?
        db_recipe = (
            db.query(recipe_model.Recipe)
            .filter(
                recipe_model.Recipe.user_id == user_id,
                recipe_model.Recipe.id == recipe.id,
            )
            .first()
        )
        db_recipe.name = recipe.name
        db_recipe.ingredients = db_ingredients
        db_recipe.procedure = recipe.procedure

        db.commit()
        db.refresh(db_recipe)
        return db_recipe

    @staticmethod
    def delete(db: Session, user_id: int, recipe: recipe_schema.Recipe):
        db.query(recipe_model.Ingredient).filter(
            recipe_model.Ingredient.recipe_id == recipe.id
        ).delete()

        db.query(recipe_model.Recipe).filter(
            recipe_model.Recipe.user_id == user_id,
            recipe_model.Recipe.name == recipe.name,
        ).delete()
        db.commit()
