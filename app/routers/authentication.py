from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Security, Header
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..authorization import oauth2, token
from ..databases import get_db, schemas


router = APIRouter(tags=["authentication"])


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = oauth2.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return
    access_token = token.create_access_token(
        data={"sub": user.username, "role_id": user.role_id}
    )
    x_token = {"Authorization": f"Bearer {access_token}"}
    return JSONResponse(headers=x_token, content="Authorization")
    # return {"access_token": access_token, "token_type": "Bearer"}


# @router.post("/login")
# async def user_login(
#     login: schemas.UserLogin = Depends(), db: Session = Depends(get_db)
# ):
#     user = oauth2.authenticate_user(login.username, login.password, db)
#     if user:
#         return JSONResponse(token.sign_jwt(login.username))
#     return {"error": "Wrong login details!"}
