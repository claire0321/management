from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session

from app.authorization import hashing
from app.authorization.token import verify_token
from app.databases import database
from app.error.exceptions import AuthBackendException
from app.routers import is_user_exist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
get_db = database.get_db


async def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user_data, user = await is_user_exist(username, db)
    if not (user or user_data):
        raise AuthBackendException(errorCode="Incorrect username", headers={"WWW-Authenticate": "Bearer"})
    if not hashing.verify(password, user_data["password"]):
        raise AuthBackendException(errorCode="Incorrect password", headers={"WWW-Authenticate": "Bearer"})
    return user_data


async def get_api_key(api_key_header: str = Security(api_key_header)):
    return verify_token(api_key_header)
