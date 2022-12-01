from sqlalchemy import Column, Integer, String, ForeignKey

from database.db import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    head_of_household_id = Column(
        Integer,
        ForeignKey("users.id"),
    )
