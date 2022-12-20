from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    Boolean,
    String,
)
from sqlalchemy.orm import relationship
from database.db import Base
from .schema import DietaryPreferenceEnum


class DietaryPreferences(Base):
    __tablename__ = "dietary_preferences"

    id = Column(Integer, primary_key=True)
    member_id = Column(ForeignKey("household_members.id"))
    preference = Column(
        Enum(DietaryPreferenceEnum),
        default=DietaryPreferenceEnum.NONE,
        nullable=False,
    )


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
    dietary_preferences = relationship(DietaryPreferences, lazy="joined")
