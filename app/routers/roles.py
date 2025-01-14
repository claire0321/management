from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.databases.database import get_db
from app.databases import role_model
from ..models import schemas

# from ..databases import get_db, models, schemas

router = APIRouter(prefix="/role", tags=["Role"])


@router.post(
    "/", status_code=201, summary="New Role created", response_model=schemas.RoleBase
)
def create_role(role: schemas.RoleBase = Depends(), db: Session = Depends(get_db)):
    role_data = role.model_dump()
    new_role = role_model.Role(**role_data)

    try:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return new_role
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role '{role.role_name}' already exists",
            response_model=schemas.RoleBase,
        )


@router.get(
    "/all_roles", response_model=List[schemas.RoleBase], status_code=status.HTTP_200_OK
)
def get_roles(db: Session = Depends(get_db)):
    return db.query(role_model.Role).all()


# @router.get("/{role}", status_code=200, response_model=schemas.RoleBase)
# def get_role(role: str, db: Session = Depends(get_db)):
#     role = "".join(role.split()).lower()
#     role_db = db.query(role_model.Role).filter(role_model.Role.name == role).first()
#
#     if not role_db:
#         raise HTTPException(status_code=409, detail=f"Role {role} not found")
#     return role_db


@router.put("/", status_code=200, response_model=schemas.RoleBase)
def update_role(
    role: str, update_role: schemas.RoleBase, db: Session = Depends(get_db)
):
    role = "".join(role.split).lower()
    role_db = db.query(role_model.Role).filter(role_model.Role.name == role).first()

    if not role_db:
        raise HTTPException(status_code=409, detail=f"Role {role} not found")

    for key, value in update_role.items():
        setattr(role_db, key, value)

    role_db.updated_at = datetime.now()
    db.commit()
    db.refresh(role_db)

    return role_db


# @router.delete("/", status_code=200)
# def delete_role(role: str, databases: Session = Depends(get_db)):
#     role = "".join(role.split).lower()
#     role_db = databases.query(models.Role).filter(models.Role.name == role).first()
#
#     if not role_db:
#         raise HTTPException(status_code=409, detail=f"Role {role} not found")
#
#     databases.delete(role)
#     databases.commit()
#     return {"message": f"Role '{role}' deleted successfully"}
