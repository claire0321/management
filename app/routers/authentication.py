from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..authorization import oauth2, token
from ..databases import get_db
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
    api_key: str = Depends(get_api_key),
):
    user = oauth2.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=token.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = token.create_access_token(
        data={"sub": user.username, "role_id": user.role_id},
        expires_delta=access_token_expires,
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    return JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}, headers=headers
    )
    # return {"access_token": access_token, "token_type": "bearer"}
