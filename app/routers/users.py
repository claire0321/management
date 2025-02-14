from typing import List, Optional

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.authorization import oauth2
from app.databases import database
from app.error import VariableException
from app.models import schemas
from app.routers import crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(oauth2.get_api_key)],
)

db_dependency = database.db_dependency


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserBase,
    response_model_exclude_unset=True,
    response_model_exclude={"password"},
    summary="새로운 회원 등록",
    description="새로운 회원의 정보를 추가 합니다.",
)
async def create_user(user: schemas.UserCreateBody, db: db_dependency):
    try:
        user_data = user.model_dump(exclude_unset=True)  # dict
        user_data["password"] = user.password  # updated user_data, dict
        await crud.create_(user_data, db)
        return user
    except:
        raise VariableException(errorCode=f"Username '{user.username}' already exists")


@router.get(
    "/",
    response_model=List[schemas.UserBase],
    status_code=status.HTTP_200_OK,
    summary="회원 목록 조회",
    description="전체 회원의 username 목록을 list 형태로 출력 합니다.",
)
async def get_users(
        db: db_dependency,
        order_by: Optional[schemas.OrderQuery] = None,
        sort_by: Optional[schemas.SortByQuery] = None,
):
    return await crud.get_s(db, order_by, sort_by)


@router.get(
    "/{username}",
    response_model=schemas.UserBase,
    status_code=status.HTTP_200_OK,
    summary="특정 회원 정보 조회",
    description="username에 해당 하는 회원 정보를 조회 합니다.",
)
async def get_user(username: str, db: db_dependency):
    return await crud.get_(username, db)


@router.put(
    "/update/",
    response_model=schemas.UserBase,
    response_model_exclude={"password"},
    status_code=status.HTTP_200_OK,
    summary="회원 정보 업데이트",
    description="username에 해당 하는 회원 정보를 수정 합니다. 수정 가능한 항목: password, email",
)
async def update_user(
        updated_user: schemas.UserUpdateBody,
        db: db_dependency,
        current_user: schemas.TokenData = Depends(oauth2.get_api_key),
):
    update_data = updated_user.model_dump(exclude_unset=True)  # dict

    return await crud.update_(db, update_data, current_user)


@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
    summary="회원 정보 삭제",
    description="username에 해당 하는 회원 정보를 삭제 합니다.",
)
async def delete_user(
        username: str,
        db: db_dependency,
):
    return await crud.delete_(db, username)


@router.put(
    "/activate",
    status_code=status.HTTP_200_OK,
    summary="회원 활성화",
    description="username에 해당 하는 회원을 활성화 합니다.",
    response_model=schemas.UserBase,
)
async def activate_user(
        username: str,
        db: db_dependency,
):
    return await crud.activate_(username, db)


@router.put(
    "/deactivate",
    status_code=status.HTTP_200_OK,
    summary="회원 비활성화",
    description="username에 해당 하는 회원을 비활성화 합니다",
)
async def deactivate_user(
        username: str,
        db: db_dependency,
):
    return await crud.deactivate_(username, db)
