from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from . import hashing
from .token import verify_token
from ..databases.database import get_db
from ..databases import user_model
from ..models import schemas
from typing import List, Any

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )
    if not user:
        return False
    if not hashing.verify(password, user.password):
        return False
    return user


async def get_current_user(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(api_key_header, credentials_exception)

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
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

def get_api_key(api_key_header: str = Security(api_key_header)):
    token_data = verify_token(api_key_header)
    return ""



class RoleChecker:
    def __init__(self, allowed_roles: List[int]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: schemas.UserInDB = Depends(get_current_active_user)) -> Any:
        if not current_user:
            return JSONResponse("Not verified account", 403)

        if current_user.role_id in self.allowed_roles:
            return True
        return JSONResponse("Insufficient Permission", 401)
    #
    # def __init__(self, allowed_roles: List[str]) -> None:
    #     self.allowed_roles = allowed_roles
    #
    # def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
    #     if not current_user.is_verified:
    #         raise AccountNotVerified()
    #     if current_user.role in self.allowed_roles:
    #         return True
    #
    #     raise InsufficientPermission()

# def check_role(required_role: int):
#     def role_checker(user: schemas.UserInDB = Depends(get_current_active_user)):
#         if user.role_id > required_role:
#             return None
#         return user
#     if role_checker is None:
#         return False
#     return True

