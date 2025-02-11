from app.databases import user_model, role_model
from app.databases.database import db_dependency
from app.databases.redis_base import redis_cache, redis_set
from app.error import FieldException, VariableException
from app.models import schemas
from app.routers import role_available, sorting_user, is_user_exist


async def create_(data: dict, db: db_dependency, types: str = "user"):
    # Create new user or role
    if types == "user":
        new_object = user_model.User(**data)  # user_model.User
        await role_available(new_object.role_id, db)
    else:  # if type is role
        new_object = role_model.Role(**data)

    try:
        db.add(new_object)
        db.commit()
        db.refresh(new_object)

        redis_set(type_=types, id_=new_object.username if types == "user" else new_object.name, data=data)
    except:
        raise


async def get_s(db: db_dependency, order_by=None, sort_by=None, types: str = "user"):
    # Get lists
    if types == "user":
        query = db.query(user_model.User).filter(user_model.User.is_active == True)
        lists = await sorting_user(query, order_by, sort_by)
    else:  # if type is role
        lists = db.query(role_model.Role).all()

    # Caching
    for val in lists:
        name = val.username if types == "user" else val.name
        cache_key = f"{types.upper()}:{name}"
        cache_data = redis_cache.get(cache_key)
        if not cache_data:
            data_ = {k: v for k, v in val.__dict__.items() if not k.startswith("_")}
            redis_set(type_=types, id_=name, data=data_)
    return lists


async def get_(username: str, db: db_dependency):
    if not "".join(username.split()):
        raise FieldException(errorCode="Username cannot be empty")
    if " " in username:
        raise FieldException(errorCode="Please provide value without any space in username")

    user_data, _ = await is_user_exist(username, db)
    return user_data


async def update_(db: db_dependency, update_data: dict,
                  current_user: schemas.TokenData, types: str = "user"):
    try:
        if types == "user":
            model = user_model.User
            value = model.username
            name: str = update_data["username"]
        else:
            model = role_model.Role
            value = model.name
            name: str = update_data["name"]

        update_db = db.query(model).filter(value == name).first()
        if not update_db:
            VariableException(errorCode=f"User {updated_user.username} not found")
        for key, value in update_data.items():
            if current_user.role_id != 1 and key == "role_id":
                raise VariableException(statusCode=403, errorCode="Must be admin to update role")
            setattr(update_db, key, value)
        db.commit()
        db.refresh(update_db)

        redis_set(types, name, update_db)

        return update_db
    except VariableException as e:
        raise e


async def delete_(db: db_dependency, name: str):
    try:
        user_data, user = is_user_exist(username, db)
        if user:
            db.delete(user)
            db.commit()
        else:
            db.query(user_model.User).filter(user_model.User.username == name).delete()
            db.commit()
        cache_user = redis_cache.get(f"USER:{name}")
        if cache_user:
            redis_cache.delete(f"USER:{name}")
        return {"message": f"User '{name}' deleted successfully"}
    except:
        raise VariableException(errorCode=f"Unable to delete {username}")
