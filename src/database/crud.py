from fastapi import HTTPException
from sqlalchemy.orm import Session

import app.pantry.model as pantry_model
import app.pantry.schema as pantry_schema
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
        db.refresh(db_user)

        new_member = household_schema.HouseholdMemberCreate(
            user_id=db_user.id,
        )
        household.add_member(
            db,
            db_user.id,
            new_member,
        )
        return db_user

    @staticmethod
    def update(db: Session, updated_user: user_schema.User):
        db_user: user_model.User = user.get(db, updated_user.id)
        db_user.first_name = updated_user.first_name
        db_user.last_name = updated_user.last_name
        db.commit()
        db.refresh(db_user)
        return db_user


class household:
    @staticmethod
    def add_member(
        db: Session,
        head_of_household_id: int,
        member: household_schema.HouseholdMemberCreate,
    ):
        if member.dietary_preferences is None:
            member.dietary_preferences = []

        diet_prefs = [
            household_model.DietaryPreferences(**e.dict())
            for e in member.dietary_preferences
        ]

        db_member = household_model.HouseholdMember(
            head_of_household_id=head_of_household_id,
            first_name=member.first_name,
            last_name=member.last_name,
            user_id=member.user_id,
            child=member.child,
            dietary_preferences=diet_prefs,
        )

        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def get_all(db: Session, user_id: int):
        db_member = (
            db.query(household_model.HouseholdMember)
            .filter(household_model.HouseholdMember.user_id == user_id)
            .first()
        )
        db_members = (
            db.query(household_model.HouseholdMember)
            .filter(
                household_model.HouseholdMember.head_of_household_id
                == db_member.head_of_household_id
            )
            .all()
        )
        for member in db_members:
            if member.user_id is not None:
                u: user_model.User = (
                    db.query(user_model.User)
                    .filter(user_model.User.id == member.user_id)
                    .first()
                )
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

        db.query(household_model.DietaryPreferences).filter(
            household_model.DietaryPreferences.member_id == member.id
        ).delete()

        diet_prefs = [
            household_model.DietaryPreferences(**e.dict())
            for e in member.dietary_preferences
        ]

        db_member.first_name = member.first_name
        db_member.last_name = member.last_name
        db_member.child = member.child
        db_member.dietary_preferences = diet_prefs
        db_member.head_of_household_id = member.head_of_household_id
        db_member.user_id = member.user_id

        db.commit()
        db.refresh(db_member)
        return db_member

    @staticmethod
    def remove_from_household(
        db: Session,
        member: household_schema.HouseholdMember,
    ):
        """
        Member must not be head of own household.  This is only for deleting
        sub-members from your household.
        """
        if member.user_id is None:
            db.query(household_model.DietaryPreferences).filter(
                household_model.DietaryPreferences.member_id == member.id
            ).delete()
            db.query(household_model.HouseholdMember).filter(
                household_model.HouseholdMember.id == member.id,
            ).delete()
            db.commit()
        else:
            member.head_of_household_id = member.user_id
            household.update(db, member)


class pantry:
    @staticmethod
    def add(db: Session, user_id: int, pantry_item: pantry_schema.PantryItemCreate):
        db_pantry_item = pantry_model.PantryItem(**pantry_item.dict())
        db_pantry_item.user_id = user_id
        db.add(db_pantry_item)
        db.commit()
        db.refresh(db_pantry_item)
        return db_pantry_item

    @staticmethod
    def get_all(db: Session, user_id: int):
        return (
            db.query(pantry_model.PantryItem)
            .filter(pantry_model.PantryItem.user_id == user_id)
            .all()
        )

    @staticmethod
    def update(db: Session, user_id: int, item: pantry_schema.PantryItem):
        db_pantry_item = (
            db.query(pantry_model.PantryItem)
            .filter(
                pantry_model.PantryItem.user_id == user_id,
                pantry_model.PantryItem.id == item.id,
            )
            .first()
        )
        db_pantry_item.name = item.name
        db_pantry_item.quantity = item.quantity
        db_pantry_item.unit = item.unit
        db_pantry_item.storage_location = item.storage_location
        db_pantry_item.date_added = item.date_added
        db_pantry_item.use_by = item.use_by

        db.commit()
        db.refresh(db_pantry_item)
        return db_pantry_item

    @staticmethod
    def delete(db: Session, user_id: int, item: pantry_schema.PantryItem):
        db.query(pantry_model.PantryItem).filter(
            pantry_model.PantryItem.user_id == user_id,
            pantry_model.PantryItem.name == item.name,
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
            servings=recipe.servings,
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
        db_recipe.servings = recipe.servings
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
