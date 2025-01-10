from typing import List, Union

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from . import is_user_exist
from ..authorization import hashing
from ..databases import schemas, get_db
from ..models import user_model

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[schemas.ShowUser, schemas.UserBase],
    response_model_exclude={"password"},
    summary="새로운 회원 등록",
    description="새로운 회원의 정보를 추가 합니다.",
)
async def create_user(
    user: schemas.UserCreate = Depends(),
    db: Session = Depends(get_db),
    # current_user: schemas.UserInDB = Depends(oauth2.check_role(2)),
):
    user_data = user.model_dump(exclude_unset=True)
    new_user = user_model.User(**user_data)
    new_user.password = hashing.bcrypt(user.password)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        if new_user.email:
            return user

        return schemas.UserBase(username=new_user.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' already exists",
        )


@router.get(
    "/",
    response_model=List[schemas.UserBase],
    status_code=status.HTTP_200_OK,
    summary="회원 목록 조회",
    description="전체 회원의 username 목록을 list 형태로 출력 합니다.",
)
async def get_users(
    db: Session = Depends(get_db),
    # current_user: schemas.UserInDB = Depends(oauth2.check_role(3)),
):
    return db.query(user_model.User).filter(user_model.User.is_active == True).all()


@router.get(
    "/{username}",
    response_model=Union[schemas.UserBase, schemas.ShowUser],
    status_code=status.HTTP_200_OK,
    summary="특정 회원 정보 조회",
    description="username에 해당 하는 회원 정보를 조회 합니다.",
)
async def get_user(
    username: str,
    db: Session = Depends(get_db),
    # current_user: schemas.UserInDB = Depends(oauth2.check_role(3)),
):
    # username = "".join(username.split()).capitalize()
    user = is_user_exist(username, True, db)
    if user.email:
        return user

    return schemas.UserBase(username=user.username, role_id=user.role_id)


@router.put(
    "/{username}/update",
    response_model=schemas.UserUpdate,
    response_model_exclude={"password"},
    status_code=status.HTTP_200_OK,
    summary="회원 정보 업데이트",
    description="username에 해당 하는 회원 정보를 수정 합니다. 수정 가능한 항목: password, email",
)
async def update_user(
    username: str,
    updated_user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    # current_user: schemas.UserInDB = Depends(oauth2.check_role(2)),
):
    # username = "".join(username.split()).capitalize()
    user = is_user_exist(username, True, db)
    update_data = updated_user.model_dump(exclude_unset=True)

    try:
        for key, value in update_data.items():
            # if not "".join(value.split()):
            #     raise HTTPException(
            #         status_code=422, detail=f"{key.capitalize()} cannot be empty"
            #     )
            if key == "password":
                value = hashing.bcrypt(value)
            # elif key == "username":
            #     value = "".join(value.split()).capitalize()
            # elif key == "email":
            #     value = "".join(value.split()).lower()
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
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
    # current_user: schemas.UserInDB = Depends(oauth2.check_role(2)),
):
    user = is_user_exist(username, True, db)
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
    # current_user: schemas.UserInDB = Depends(oauth2.check_role(2)),
):
    # username = username.capitalize()
    user = is_user_exist(username, False, db)
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
    # current_user: schemas.UserInDB = Depends(oauth2.get_current_active_user),
):
    user = is_user_exist(username, True, db)

    try:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return {"message": f"User '{username}' is deactivated"}
    except:
        raise HTTPException
