from typing import List, Optional

from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.authorization import oauth2
from app.databases import user_model, database
from app.error import UserException
from app.models import schemas
from app.redis import redis_cache, redis_set
from app.routers import is_user_exist, role_available, sorting_user

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
    user_data = user.model_dump(exclude_unset=True)  # dict
    user_data["password"] = user.password  # updated user_data, dict
    new_user = user_model.User(**user_data)  # user_model.User
    role_available(user.role_id, db)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        redis_set(id_=user.username, data=user_data)

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
    db: db_dependency,
    order_by: Optional[schemas.OrderQuery] = None,
    sort_by: Optional[schemas.SortByQuery] = None,
):
    query = db.query(user_model.User).filter(user_model.User.is_active == True)
    users = sorting_user(sort_by, order_by, query)

    # Caching into redis
    for user in users:
        cache_key = f"USER:{user.username}"
        cache_data = redis_cache.get(cache_key)
        if not cache_data:
            user_data = {k: v for k, v in user.__dict__.items() if not k.startswith("_")}
            redis_set(id_=user.username, data=user_data)
    return users


@router.get("/redis/test")
async def test():
    return redis_cache


@router.get(
    "/{username}",
    response_model=schemas.UserBase,
    status_code=status.HTTP_200_OK,
    summary="특정 회원 정보 조회",
    description="username에 해당 하는 회원 정보를 조회 합니다.",
)
async def get_user(username: str, db: db_dependency):
    if not "".join(username.split()):
        raise FieldException(errorCode="Username cannot be empty")
    if " " in username:
        raise FieldException(
            errorCode="Validation Error. Please provide value without any space in Username."
        )
    user_data, _ = is_user_exist(username=username, db=db)
    print(redis_cache.info(section="memory"))
    return user_data


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
    current_role = current_user.role_id
    username = updated_user.username
    if " " in username:
        raise FieldException(
            errorCode="Validation Error. Please provide value without any space in Username."
        )

    user_data, user = is_user_exist(username=username, db=db)  # user_model.User
    update_data = updated_user.model_dump(exclude_unset=True)  # dict

    try:
        if not user:
            user = db.query(user_model.User).filter(user_model.User.username == username).first()
        for key, value in update_data.items():
            if value:
                if key == "role_id" and current_role != 1:
                    raise UserException(statusCode=403, errorCode="Must be admin to update role")
                user_data[key] = value
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
    db: db_dependency,
):
    user_data, user = is_user_exist(username=username, db=db)
    try:
        if user:
            db.delete(user)
            db.commit()
        else:
            db.query(user_model.User).filter(user_model.User.username == username).delete()
            db.commit()

        cache_user = redis_cache.get(f"USER:{username}")
        if cache_user:
            redis_cache.delete(f"USER:{username}")
        return {"message": f"User '{username}' deleted successfully"}
    except:
        raise UserException(errorCode=f"Unable to delete {username}")


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
    user_data, user = is_user_exist(username, db, active_status=False)
    try:
        user_data["is_active"] = True
        if user:
            user.is_active = True
            db.commit()
            db.refresh(user)
        else:
            db.query(user_model.User).filter_by(username=username).update({"is_active": True})
            db.commit()

        redis_set(id_=username, data=user_data)

        return {"message": f"User '{username}' is activated"}
        # return {"message": f"User '{username}' is deactivated"}
    except UserException:
        raise UserException(errorCode="Invalid values to be updated")


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
    user_data, user = is_user_exist(username, db)

    try:
        user_data["is_active"] = False
        if user:
            user.is_active = False
            db.commit()
            db.refresh(user)
        else:
            db.query(user_model.User).filter_by(username=username).update({"is_active": False})
            db.commit()

        redis_set(id_=username, data=user_data)

        return {"message": f"User '{username}' is deactivated"}
    except:
        raise UserException(errorCode="Invalid values to be updated")
