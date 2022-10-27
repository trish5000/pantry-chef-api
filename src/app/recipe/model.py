from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship

from database.db import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    name = Column(String)
    quantity = Column(Float)
    unit = Column(String)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    procedure = Column(Text, nullable=True)
    timestamp = Column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP")
    )

    ingredients = relationship(Ingredient, lazy="joined")
