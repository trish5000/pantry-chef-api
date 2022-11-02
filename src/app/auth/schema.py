from typing import Optional
from pydantic import BaseModel

from app.user.schema import User


class AuthenticateRequest(BaseModel):
    token: str


class AuthenticateResponse(BaseModel):
    access_token: Optional[str]
    user: Optional[User]
    new_user: Optional[bool]
