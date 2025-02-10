from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.authorization import oauth2
from app.databases import role_model, database
from app.databases.redis_base import redis_cache, redis_set
from app.error import RoleException, UserException
from app.models import schemas

router = APIRouter(prefix="/role", tags=["Role"], dependencies=[Depends(oauth2.get_api_key)])

get_db = database.get_db


@router.post("/", status_code=201, summary="New Role created", response_model=schemas.RoleBase)
def create_role(role: schemas.RoleBase, db: Session = Depends(get_db)):
    role_data = role.model_dump(exclude_unset=True)
    new_role = role_model.Role(**role_data)

    try:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)

        redis_set(type_="ROLE", id_=role.name, data=role_data)

        return new_role
    except:
        raise RoleException(errorCode=f"Role '{role.name}' already exists")


@router.get("/all_roles", response_model=List[schemas.RoleBase], status_code=status.HTTP_200_OK)
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(role_model.Role).all()
    for role in roles:
        cache_key = f"ROLE:{role.name}"
        cache_data = redis_cache.get(cache_key)
        if not cache_data:
            role_data = {k: v for k, v in user.__dict__.items() if not k.startswith("_")}
            redis_set(type_="ROLE", id_=role.name, data=role_data)
    return roles


@router.put("/", status_code=200, response_model=schemas.RoleBase)
def update_role(
    role: str,
    update_role: schemas.RoleBase,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_api_key),
):
    if current_user.role_id != 1:
        raise UserException(statusCode=403, errorCode="Must be admin to update role")
    try:
        role_db = db.query(role_model.Role).filter(role_model.Role.name == role).first()

        if not role_db:
            raise RoleException(status_code=409, detail=f"Role {role} not found")

        for key, value in update_role.items():
            setattr(role_db, key, value)

        role_db.updated_at = datetime.now()
        db.commit()
        db.refresh(role_db)

        return role_db
    except:
        raise
