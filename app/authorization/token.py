from datetime import datetime, timedelta, timezone
from functools import lru_cache

import jwt

from app.config import JWTSetting
from app.error.exceptions import AuthBackendException
from app.models import schemas


@lru_cache()
def jwt_settings():
    return JWTSetting()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(jwt_settings().ACCESS_TOKEN_EXPIRE_MINUTES))
    # expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_settings().SECRET_KEY, algorithm=jwt_settings().ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, jwt_settings().SECRET_KEY, algorithms=[jwt_settings().ALGORITHM])
        username: str = payload.get("sub")
        role_id: int = payload.get("role_id")
        return schemas.TokenData(username=username, role_id=role_id)
    except jwt.InvalidTokenError:
        raise AuthBackendException(statusCode=403, errorCode="Invalid Token")
