from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.food_item import model as food_item_model
from app.food_item import schema as food_item_schema
from app.recipe import model as recipe_model
from app.recipe import schema as recipe_schema
from app.user import model as user_model
from app.user import schema as user_schema


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
        return db_user

    @staticmethod
    def update(db: Session, updated_user: user_schema.User):
        db_user = user.get(db, updated_user.id)
        db_user.first_name = updated_user.first_name
        db_user.last_name = updated_user.last_name
        db.commit()
        db.refresh(db_user)
        return db_user


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
