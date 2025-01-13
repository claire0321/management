import os
from datetime import datetime, timedelta, timezone
from typing import Dict
import time

import jwt
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.x509 import load_pem_x509_certificate
from dotenv import load_dotenv
from jwt import InvalidTokenError
from starlette.responses import JSONResponse

from ..databases import schemas

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
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
    except InvalidTokenError:
        return JSONResponse(
            status_code=403,
            content="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )







