from dataclasses import dataclass
from typing import Optional


### TOD: dataclass 디코레이터 있는데 굳이 __init__ 한 이유?
@dataclass
class AuthBackendException(Exception):
    unauthorized_value = 401
    statusCode: Optional[int] = unauthorized_value
    errorCode: Optional[str] = "UNAUTHORIZED"

    def __init__(self, statusCode=None, errorCode=None):
        if statusCode:
            self.statusCode: int = statusCode
        if errorCode:
            self.errorCode: str = errorCode


@dataclass
class UserException(Exception):
    """This is the base class for all user errors"""

    username: Optional[str] = None


class UserNotFound(UserException):
    """User Not found"""

    pass


class UserAlreadyExists(UserException):
    """User has provided an email for a user who exists during sign up."""

    pass


class UserAlreadyInActive(UserException):
    """User already in active status"""

    pass


@dataclass
class FieldException(Exception):
    """This is the base class for all field errors"""

    field: Optional[str] = None


class EmptyField(FieldException):
    """Provided Empty Data"""

    pass


class InvalidUsername(FieldException):
    """Invalid username having alphanum"""

    pass


class InvalidDataType(FieldException):
    """Invalid data type"""

    pass


class InsufficientSpace(FieldException):
    """Should not have a space"""

    pass


# =====================================================================

#
# class InvalidCredentials(UserException):
#     """User has provided wrong email or password during log in."""
#
#     pass


class InvalidToken(UserException):
    """User has provided an invalid or expired token"""

    pass


#
#
# class RevokedToken(UserException):
#     """User has provided a token that has been revoked"""
#
#     pass
#
#
# class AccessTokenRequired(UserException):
#     """User has provided a refresh token when an access token is needed"""
#
#     pass
#
#
# class RefreshTokenRequired(UserException):
#     """User has provided an access token when a refresh token is needed"""
#
#     pass
#
#
# class InsufficientPermission(UserException):
#     """User does not have the neccessary permissions to perform an action."""
#
#     pass
#
#
class RoleNotFound(UserException):
    """Role Not found"""

    pass


#
#
# class RoleAlreadyExists(UserException):
#     """Role already exists"""
#
#     pass
#
#
# class AccountNotVerified(Exception):
#     """Account not yet verified"""
#
#     pass
