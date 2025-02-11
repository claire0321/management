from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.authorization import hashing
from app.error import VariableException
from app.error.exceptions import (
    FieldException,
)


def validate(values: dict):
    excluded_fields = {"role_id", "is_active"}
    for field, value in values.items():
        # Skip excluded fields
        if field in excluded_fields:
            if (field == "role_id" and not isinstance(value, int)) or (
                    field == "is_active" and not isinstance(value, bool)
            ):
                raise FieldException(errorCode="Validation Error. Please provide a valid data type.")
            continue

        # Check if the value is empty or consists of only whitespace
        if value and not "".join(value.split()):
            raise FieldException(errorCode=f"{field} cannot be empty")

        # Check if the value contains any space
        if " " in value:
            raise FieldException(
                errorCode=f"Validation Error. Please provide value without any space in {field}."
            )

        # Check if username is alphanum
        if field == "username" and not value.isalnum():
            raise FieldException(errorCode="Username should be alphanum.")

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


class UserCreateBody(UserBase):
    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def model_validations(cls, values):
        username = values.get("username")
        password = values.get("password")

        if not username:
            raise FieldException(errorCode=f"Field 'username' is missing or required.")

        if not password:
            raise FieldException(errorCode=f"Field 'password' is missing or required.")
        return validate(values)


class UserUpdateBody(BaseModel):
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


class OrderQuery(str, Enum):
    asc = "asc"
    desc = "desc"


class SortByQuery(str, Enum):
    username = "username"
    role_id = "role_id"


# ============================================================================


class RoleBase(BaseModel):
    name: str
    description: str


# ============================================================================


class Token(BaseModel):
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
        raise VariableException(errorCode=f"Role for '{username}' not found")
