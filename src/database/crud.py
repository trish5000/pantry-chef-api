from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.food_item import model as food_item_model
from app.food_item import schema as food_item_schema
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
