from app.databases import user_model, role_model
from app.databases.database import db_dependency
from app.databases.redis_base import redis_set, redis_get, redis_delete
from app.error import FieldException, VariableException
from app.models import schemas
from app.routers import role_available, sorting_user, is_user_exist


async def create_(data: dict, db: db_dependency, types: str = "user"):
    # Create new user or role
    if types == "user":
        new_object = user_model.User(**data)  # user_model.User
        name = new_object.username
    else:  # if type is role
        new_object = role_model.Role(**data)
        name = new_object.name
    try:
        db.add(new_object)
        db.commit()
        db.refresh(new_object)

        redis_set(type_=types, id_=name, db=new_object)
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
    for var in lists:
        name = var.username if types == "user" else var.name
        if not redis_get(name=name):
            redis_set(types, name, var)
    return lists


async def get_(username: str, db: db_dependency):
    if not "".join(username.split()):
        raise FieldException(errorCode="Username cannot be empty")
    if " " in username:
        raise FieldException(errorCode="Please provide value without any space in username")

    user_data, _ = await is_user_exist(username, db)
    return user_data


async def update_(db: db_dependency, update_data: dict, current_user: schemas.TokenData, types: str = "user"):
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
            VariableException(errorCode=f"User {update_db.username} not found")
        for key, value in update_data.items():
            if key == "role_id":
                if current_user.role_id != 1:
                    raise VariableException(statusCode=403, errorCode="Must be admin to update role")
                else:
                    await role_available(value, db)
            setattr(update_db, key, value)
        db.commit()
        db.refresh(update_db)

        redis_set(types, name, update_db)

        return update_db
    except VariableException as e:
        raise e


async def delete_(db: db_dependency, name: str):
    try:
        db.query(user_model.User).filter(user_model.User.username == name).delete()
        db.commit()

        cache_user = redis_get(name=name)
        user_data, user = is_user_exist(name, db)
        if user:
            db.delete(user)
            db.commit()
        else:
            db.query(user_model.User).filter(user_model.User.username == name).delete()
            db.commit()
        cache_user = redis_cache.get(f"USER:{name}")
        if cache_user:
            redis_delete(f"USER:{name}")
        return {"message": f"User '{name}' deleted successfully"}
    except:
        raise VariableException(errorCode=f"Unable to delete {name}")


async def activate_(username: str, db: db_dependency):
    try:
        user = db.query(user_model.User).filter_by(username=username).first()
        if not user:
            raise
    except:
        raise VariableException(errorCode=f"User '{username}' not Found")

    try:
        user.is_active = True
        db.commit()
        db.refresh(user)

        redis_set(id_=username, db=user)
        return user
    except VariableException:
        raise VariableException(errorCode="Invalid values to be updated")


async def deactivate_(username: str, db: db_dependency):
    try:
        user = db.query(user_model.User).filter_by(username=username).first()
        if not user:
            raise
    except:
        raise VariableException(errorCode=f"User '{username}' not Found")

    try:
        if not user:
            raise VariableException(errorCode=f"User '{username}' not Found")
        user.is_active = False
        db.commit()
        db.refresh(user)

        redis_delete(f"USER:{username}")

        return {"message": f"User '{username}' is deactivated"}
    except VariableException:
        raise VariableException(errorCode="Invalid values to be updated")
        raise VariableException(errorCode=f"Unable to delete {name}")
