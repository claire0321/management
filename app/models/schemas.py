from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.authorization import hashing
from app.error.exceptions import EmptyField, InvalidUsername, InvalidDataType, InsufficientSpace


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
    email: Optional[EmailStr] = None
    role_id: int = 3
    password: Annotated[str, Field(exclude=True)]
    is_active: Annotated[bool, Field(exclude=True)] = True

    class Config:
        from_attributes = True

        model_config = {
            "json_schema_extra": {
                "example": {
                    "username": "Bob",
                    "email": "Bob@example.com",
                    "password": "password",
                    "role_id": 1,
                }
            }
        }


class UserCreate(UserBase):
    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def field_validations(cls, values):
        return validate(values)


class UserUpdate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[int] = None

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def field_validations(cls, values):
        return validate(values)


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
