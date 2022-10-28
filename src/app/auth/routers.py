from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app.config import Settings, get_settings

from app.user import model
from .schema import AuthenticateRequest
from database import auth, db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_authenticated_user(token=Depends(oauth2_scheme)):
    try:
        user = jwt.decode(token, key="myKey", algorithms=["HS256"])
        return user
    except jwt.DecodeError:
        raise HTTPException(403, "Invalid token")


@router.post("/auth/authenticate")
async def authenticate(
    auth_request: AuthenticateRequest,
    session: Session = Depends(db.get_db),
    settings: Settings = Depends(get_settings),
):
    return auth.auth.authenticate(
        session,
        auth_request,
        settings,
    )


# TODO: Remove this later
@router.get("/auth/spoof/{user_id}")
async def spoof_user(
    user_id: int,
    session: Session = Depends(db.get_db),
    settings: Settings = Depends(get_settings),
):
    print("HERE!")
    db_user = session.query(model.User).filter(model.User.id == user_id).first()

    print(db_user)

    access_token_data: dict = {
        "sub": db_user.id,
        "user_id": db_user.id,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
    }
    return auth.auth.create_access_token(access_token_data, settings)
