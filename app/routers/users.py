from typing import List, Optional, Annotated

from fastapi import APIRouter, status, Depends, HTTPException, Body
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from app.authorization import oauth2
from app.databases import user_model, database
from app.error.exceptions import EmptyField, InsufficientSpace, UserAlreadyExists
from app.models import schemas
from app.routers import is_user_exist

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(oauth2.get_api_key)],
)

get_db = database.get_db


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserBase,
    response_model_exclude_unset=True,
    response_model_exclude={"password"},
    summary="새로운 회원 등록",
    description="새로운 회원의 정보를 추가 합니다.",
)
async def create_user(
    user: Annotated[
        schemas.UserCreate,
        Body(
            examples=[
                {
                    "username": "username",
                    "password": "password",
                    "email": "user@example.com",
                    "role_id": 3,
                }
            ]
        ),
    ],
    db: Session = Depends(get_db),
):
    user_data = user.model_dump(exclude_unset=True)
    user_data["password"] = user.password
    new_user = user_model.User(**user_data)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return user
    except:
        raise UserAlreadyExists(user.username)


@router.get(
    "/",
    response_model=List[schemas.UserBase],
    status_code=status.HTTP_200_OK,
    summary="회원 목록 조회",
    description="전체 회원의 username 목록을 list 형태로 출력 합니다.",
)
async def get_users(order_by: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(user_model.User).filter(user_model.User.is_active == True)
    if order_by == "desc":
        return query.order_by(desc(user_model.User.username)).all()
    else:
        return query.order_by(asc(user_model.User.username)).all()


@router.get(
    "/{username}",
    response_model=schemas.UserBase,
    status_code=status.HTTP_200_OK,
    summary="특정 회원 정보 조회",
    description="username에 해당 하는 회원 정보를 조회 합니다.",
)
async def get_user(
    username: str,
    db: Session = Depends(get_db),
):
    if not "".join(username.split()):
        raise EmptyField("Username")
    if " " in username:
        raise InsufficientSpace("Username")
    return is_user_exist(username=username, db=db)


@router.put(
    "/{username}/update",
    response_model=schemas.UserBase,
    response_model_exclude={"password"},
    status_code=status.HTTP_200_OK,
    summary="회원 정보 업데이트",
    description="username에 해당 하는 회원 정보를 수정 합니다. 수정 가능한 항목: password, email",
)
async def update_user(
    updated_user: schemas.UserUpdate,
    db: Session = Depends(get_db),
):
    username = updated_user.username
    if " " in username:
        raise InsufficientSpace("Username")
    user = is_user_exist(username=username, db=db)
    update_data = updated_user.model_dump(exclude_unset=True)

    try:
        for key, value in update_data.items():
            if value:
                # if key == "password":
                #     value = hashing.bcrypt(value)
                setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user
    except:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid values to be updated",
        )


@router.delete(
    "/{username}/delete",
    status_code=status.HTTP_200_OK,
    summary="회원 정보 삭제",
    description="username에 해당 하는 회원 정보를 삭제 합니다.",
)
async def delete_user(
    username: str,
    db: Session = Depends(get_db),
):
    user = is_user_exist(username=username, db=db)
    db.delete(user)
    db.commit()
    return {"message": f"User '{username}' deleted successfully"}


@router.put(
    "/{username}/activate",
    status_code=status.HTTP_200_OK,
    summary="회원 활성화",
    description="username에 해당 하는 회원을 활성화 합니다.",
)
async def activate_user(
    username: str,
    db: Session = Depends(get_db),
):
    user = is_user_exist(username, db, active_status=False)
    try:
        user.is_active = True
        db.commit()
        db.refresh(user)
        return {
            "message": f"User '{username}' is activated",
            "username": username,
            "email": user.email,
            "role_id": user.role_id,
        }
    except:
        raise HTTPException


@router.put(
    "/{username}/deactivate",
    status_code=status.HTTP_200_OK,
    summary="회원 비활성화",
    description="username에 해당 하는 회원을 비활성화 합니다",
)
async def deactivate_user(
    username: str,
    db: Session = Depends(get_db),
):
    username = username
    user = is_user_exist(username, db)

    try:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return {"message": f"User '{username}' is deactivated"}
    except:
        raise HTTPException
