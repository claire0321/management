from datetime import datetime, timedelta, timezone

import jwt

from app import jwt_settings
from app.error.exceptions import InvalidToken
from app.models import schemas


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])
        username: str = payload.get("sub")
        role_id: int = payload.get("role_id")
        return schemas.TokenData(username=username, role_id=role_id)
    except jwt.InvalidTokenError:
        raise InvalidToken
