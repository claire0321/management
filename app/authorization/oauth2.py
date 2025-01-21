from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session

from app.authorization import hashing
from app.authorization.token import verify_token
from app.databases import database, user_model

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
get_db = database.get_db

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )
    if not user:
        return False
    if not hashing.verify(password, user.password):
        return False
    return user

def get_api_key(api_key_header: str = Security(api_key_header)):
    return verify_token(api_key_header)