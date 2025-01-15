from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.authorization import oauth2, token
from app.databases.database import get_db

router = APIRouter(tags=["authentication"])


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = oauth2.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return
    access_token = token.create_access_token(data={"sub": user.username, "role_id": user.role_id})
    x_token = {"Authorization": f"Bearer {access_token}"}
    return JSONResponse(headers=x_token, content="Authorization")
