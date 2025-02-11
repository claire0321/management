from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.authorization import oauth2
from app.databases import database
from app.error import VariableException
from app.models import schemas
from app.routers import crud

router = APIRouter(prefix="/role", tags=["Role"], dependencies=[Depends(oauth2.get_api_key)])

get_db = database.get_db


@router.post("/", status_code=201, summary="New Role created", response_model=schemas.RoleBase)
async def create_role(role: schemas.RoleBase, db: Session = Depends(get_db)):
    try:
        await crud.create_(role.model_dump(exclude_unset=True), db, "role")
        return role
    except:
        raise VariableException(errorCode=f"Role '{role.name}' already exists")


@router.get("/all_roles", response_model=List[schemas.RoleBase], status_code=status.HTTP_200_OK)
async def get_roles(db: Session = Depends(get_db)):
    return await crud.get_s(db, types="role")


@router.put("/", status_code=200, response_model=schemas.RoleBase)
async def update_role(
        update_role: schemas.RoleBase,
        db: Session = Depends(get_db),
        current_user: schemas.TokenData = Depends(oauth2.get_api_key),
):
    try:
        update_data = update_role.model_dump(exclude_unset=True)
        return await crud.update_(db, update_data, current_user, "role")
    except VariableException as e:
        if not e.errorCode:
            raise VariableException(errorCode=f"Role {update_role.name} not found")
        else:
            raise e
