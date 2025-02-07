from typing import List, Optional

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.authorization import oauth2
from app.databases import user_model, database
from app.error import UserException
from app.models import schemas
from app.routers import is_user_exist, role_available, sorting_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
async def create_user(user: schemas.UserCreateBody, db: Session = Depends(get_db)):
    user_data = user.model_dump(exclude_unset=True)
    user_data["password"] = user.password
    new_user = user_model.User(**user_data)
    role_available(user.role_id, db)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return user
    except:
        raise UserException(errorCode=f"Username '{user.username}' already exists")


@router.get(
    "/",
    response_model=List[schemas.UserBase],
    status_code=status.HTTP_200_OK,
    summary="회원 목록 조회",
    description="전체 회원의 username 목록을 list 형태로 출력 합니다.",
)
async def get_users(
    order_by: Optional[schemas.OrderQuery] = None,
    sort_by: Optional[schemas.SortByQuery] = None,
    db: Session = Depends(get_db),
):
    query = db.query(user_model.User).filter(user_model.User.is_active == True)

    return sorting_user(sort_by, order_by, query)


from app.redis import redis_cache


@router.get("/redis/test")
async def test():
    rd = redis_cache
    return {rd}


@router.get(
    "/{username}",
    response_model=schemas.UserBase,
    status_code=status.HTTP_200_OK,
    summary="특정 회원 정보 조회",
    description="username에 해당 하는 회원 정보를 조회 합니다.",
)
async def get_user(username: str, db: Session = Depends(get_db)):
    if not "".join(username.split()):
        raise FieldException(errorCode="Username cannot be empty")
    if " " in username:
        raise FieldException(
            errorCode="Validation Error. Please provide value without any space in Username."
        )
    return is_user_exist(username=username, db=db)


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
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_api_key),
):
    current_role = current_user.role_id
    username = updated_user.username
    if " " in username:
        raise FieldException(
            errorCode="Validation Error. Please provide value without any space in Username."
        )
    user = is_user_exist(username=username, db=db)
    update_data = updated_user.model_dump(exclude_unset=True)

    try:
        for key, value in update_data.items():
            if value:
                if key == "role_id" and current_role != 1:
                    raise UserException(statusCode=403, errorCode="Must be admin to update role")
                setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user
    except UserException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while updating the user: {str(e)}")


@router.delete(
    "/delete",
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
    cache_user = redis_cache.get(f"Users:{username}")
    if cache_user:
        redis_cache.delete(f"Users:{username}")
    return {"message": f"User '{username}' deleted successfully"}


@router.put(
    "/activate",
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
        raise UserException(errorCode="Invalid values to be updated")


@router.put(
    "/deactivate",
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
        raise UserException(errorCode="Invalid values to be updated")
