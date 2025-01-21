from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.authorization import hashing
from app.error.exceptions import EmptyField, InvalidUsername, InvalidDataType, InsufficientSpace, MissingValue
from app.error.exceptions import RoleNotFound


def validate(values: dict):
    excluded_fields = {"role_id", "is_active"}
    for field, value in values.items():
        # Skip excluded fields
        if field in excluded_fields:
            if (field == "role_id" and not isinstance(value, int)) or (
                field == "is_active" and not isinstance(value, bool)
            ):
                raise InvalidDataType
            continue

        # Check if the value is empty or consists of only whitespace
        if value and not "".join(value.split()):
            raise EmptyField(field)

        # Check if the value contains any space
        if " " in value:
            raise InsufficientSpace(field)

        # Check if username is alphanum
        if field == "username" and not value.isalnum():
            raise InvalidUsername

        # Hash password
        if field == "password" and value:
            values["password"] = hashing.bcrypt("".join(value.split()))
    return values


class UserBase(BaseModel):
    username: str
    password: Annotated[str, Field(exclude=True)]
    email: Optional[EmailStr] = None
    role_id: int = 3
    is_active: Annotated[bool, Field(exclude=True)] = True

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def model_validations(cls, values):
        username = values.get("username")
        password = values.get("password")

        if not username:
            raise MissingValue("username")

        if not password:
            raise MissingValue("password")
        return validate(values)


class UserUpdate(BaseModel):
    username: str
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def model_validations(cls, values):
        return validate(values)


# ============================================================================


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


class SortBy(str, Enum):
    username = "username"
    role_id = "role_id"


# ============================================================================


class RoleBase(BaseModel):
    name: str
    description: str


# ============================================================================


class Token(BaseModel):
    # Authorization: str = None
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role_id: Optional[int] = None

    @classmethod
    def get_role_name(cls, username: str, role_id: int):
        if role_id == 1:
            return "admin"
        elif role_id == 2:
            return "manager"
        elif role_id == 3:
            return "general"
        raise RoleNotFound(token_name=username)
