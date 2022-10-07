from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, text
from app.food_item.schema import StorageLocation

from database.db import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Float)
    storage_location = Column(Enum(StorageLocation))
    date_added = Column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP")
    )
    use_by = Column(DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP"))
    timestamp = Column(
        DateTime(timezone=False), server_default=text("CURRENT_TIMESTAMP")
    )
    unit = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
