from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, model_validator

from app.authorization import hashing


def validate(values):
    for field, value in values.items():
        if field != "role_id":
            if value:
                if not "".join(value.split()):
                    raise HTTPException(
                        status_code=422, detail=f"{field.capitalize()} cannot be empty"
                    )
                if field == "password" and value:
                    values["password"] = hashing.bcrypt("".join(value.split()))
    return values


class UserBase(BaseModel):
    username: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    email: EmailStr | None = None
    password: str
    role_id: int = 3

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def field_validations(cls, values):
        return validate(values)


class ShowUser(UserBase):
    email: EmailStr | None = None
    role_id: int


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    role_id: int | None = None


class UserInDB(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str
    role_id: int
    is_active: bool = True


class UserLogin(BaseModel):
    username: str = Field()
    password: str = Field()


# ============================================================================


class RoleBase(BaseModel):
    name: str
    description: str


class RoleName(RoleBase):
    role_id: int


# ============================================================================


# class Login(BaseModel):
#     email: str
#     password: str


class Token(BaseModel):
    # Authorization: str = None
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    role_id: int | None = None
