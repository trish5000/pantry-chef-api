from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    Boolean,
    ARRAY,
    String,
)
from database.db import Base
from .schema import DietaryPreferences


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )
    head_of_household_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    child = Column(Boolean, default=False)
    dietary_preferences = Column(
        ARRAY(
            Enum(
                DietaryPreferences,
                create_constraint=False,
                native_enum=False,
            ),
        ),
    )
