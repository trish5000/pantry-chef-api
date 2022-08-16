from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, text

from database.db import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Float)
    timestamp = Column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP")
    )
    unit = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
