import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from starlette.responses import JSONResponse

from app.models import schemas

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def create_access_token(data: dict):
    to_encode = data.copy
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role_id: int = payload.get("role_id")
        if username is None:
            return JSONResponse(
                status_code=403,
                content="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return schemas.TokenData(username=username, role_id=role_id)
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=403,
            content="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
