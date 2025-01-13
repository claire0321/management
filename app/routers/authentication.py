from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Security, Header
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..authorization import oauth2, token
from ..databases import get_db, schemas
from fastapi.security.api_key import APIKeyHeader


router = APIRouter(tags=["authentication"])

API_KEY = "your-secret-api-key"
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        return JSONResponse(None, 403)


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    # api_key: str = Depends(get_api_key),
    # x_token: Annotated[str, None, Header()] = None,
):
    user = oauth2.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return
    access_token = token.create_access_token(
        data={"sub": user.username, "role_id": user.role_id},
        expires_delta=timedelta(minutes=token.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    x_token = {"Authenticate": f"Bearer {access_token}"}
    return JSONResponse(headers=x_token, content="Authenticated")


# @router.post("/login")
# async def user_login(
#     login: schemas.UserLogin = Depends(), db: Session = Depends(get_db)
# ):
#     user = oauth2.authenticate_user(login.username, login.password, db)
#     if user:
#         return JSONResponse(token.sign_jwt(login.username))
#     return {"error": "Wrong login details!"}
