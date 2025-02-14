from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthBackendException(Exception):
    unauthorized_value = 401
    statusCode: Optional[int] = unauthorized_value
    errorCode: Optional[str] = "UNAUTHORIZED"
    headers: Optional[dict] = None


@dataclass
class FieldException(Exception):
    """This is the base class for all field errors"""

    statusCode: Optional[int] = 422
    errorCode: Optional[str] = None


@dataclass
class VariableException(Exception):
    """This is the base class for all user and role errors"""

    statusCode: Optional[int] = 409
    errorCode: Optional[str] = None


@dataclass
class RedisException(Exception):
    statusCode: Optional[int] = 422
    errorCode: Optional[str] = None
