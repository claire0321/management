from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import hashing
from .token import verify_token
from ..databases import get_db, schemas
from ..models import user_model

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )
    if not user:
        return False
    if not hashing.verify(password, user.password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)

    user = (
        db.query(user_model.User)
        .filter(user_model.User.username == token_data.username)
        .first()
    )
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.UserInDB = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(admin_user: schemas.UserInDB = Depends(get_current_active_user)):
    if admin_user.role_id != 1:
        raise HTTPException(status_code=400, detail="Permission denied")
    return admin_user

async def get_manager_user(manager_user: schemas.UserInDB = Depends(get_current_active_user)):
    if manager_user.role_id != 2:
        raise HTTPException(status_code=400, detail="Permission denied")
    return manager_user



