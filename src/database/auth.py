from fastapi import HTTPException

import jwt
from sqlalchemy.orm import Session

from app.auth import schema
from app.config import Settings
from app.user import model
from google.oauth2 import id_token
from google.auth.transport import requests


class auth:
    @staticmethod
    def create_access_token(data: dict, settings: Settings):
        encoded_jwt = jwt.encode(data, settings.token_key)
        return encoded_jwt

    @staticmethod
    def authenticate(
        db: Session,
        request: schema.AuthenticateRequest,
        settings: Settings,
    ):
        valid_client_ids = [
            settings.oauth_android_client_id,
            settings.oauth_ios_client_id,
            settings.oauth_android_client_id,
            settings.oauth_desktop_client_id,
        ]

        idinfo = id_token.verify_oauth2_token(request.token, requests.Request())

        if idinfo["aud"] not in valid_client_ids:
            raise HTTPException(status_code=401, detail="Invalid token")

        has_email = len(idinfo["email"]) > 0 and idinfo["email_verified"]
        if not has_email:
            raise HTTPException(
                status_code=400, detail="Token has missing/invalid email"
            )

        validated_email = idinfo["email"]
        db_user = (
            db.query(model.User).filter(model.User.email.ilike(validated_email)).first()
        )

        new_user = False
        if db_user is None:
            new_user = True
            db_user = model.User(
                email=validated_email,
                first_name=idinfo["given_name"],
                last_name=idinfo["family_name"],
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        access_token_data: dict = {
            "sub": db_user.id,
            "user_id": db_user.id,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
        }
        encoded_jwt = auth.create_access_token(access_token_data, settings)

        return schema.AuthenticateResponse(
            access_token=encoded_jwt,
            user=db_user,
            new_user=new_user,
        )
