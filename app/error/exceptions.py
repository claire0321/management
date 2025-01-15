from dataclasses import dataclass
from typing import Optional


@dataclass
class UserException(Exception):
    """This is the base class for all user errors"""

    username: str


class UserNotFound(UserException):
    """User Not found"""

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


# =====================================================================


class InvalidToken(UserException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(UserException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(UserException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(UserException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(UserException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(UserException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(UserException):
    """User does not have the neccessary permissions to perform an action."""

    pass


class RoleNotFound(UserException):
    """Role Not found"""

    pass


class RoleAlreadyExists(UserException):
    """Role already exists"""

    pass


class AccountNotVerified(Exception):
    """Account not yet verified"""

    pass


#
# def create_exception_handler(
#     status_code: int, initial_detail: Any
# ) -> Callable[[Request, Exception], JSONResponse]:
#     async def exception_handler(request: Request, exc: UserException):
#         return JSONResponse(content=initial_detail, status_code=status_code)
#
#     return exception_handler
#
#
# def register_all_errors(app: FastAPI):
#     app.add_exception_handler(
#         UserAlreadyExists,
#         create_exception_handler(
#             status_code=HTTP_403_FORBIDDEN,
#             initial_detail={
#                 "message": "User with email already exists",
#                 "error_code": "user_exists",
#             },
#         ),
#     )
#
#     app.add_exception_handler(
#         UserNotFound,
#         create_exception_handler(
#             status_code=HTTP_404_NOT_FOUND,
#             initial_detail={
#                 "message": "User not found",
#                 "error_code": "user_not_found",
#             },
#         ),
#     )
#
#
# class StatusCode:
#     HTTP_500 = 500
#     HTTP_400 = 400
#     HTTP_401 = 401
#     HTTP_403 = 403
#     HTTP_404 = 404
#     HTTP_405 = 405
#     HTTP_409 = 409
#
#
# class APIException(Exception):
#     status_code: int
#     code: str
#     msg: str
#     detail: str
#
#     def __init__(
#         self,
#         *,
#         status_code: int = StatusCode.HTTP_500,
#         code: str = "000000",
#         msg: str = None,
#         detail: str = None,
#         ex: Exception = None,
#     ):
#         self.status_code = status_code
#         self.code = code
#         self.msg = msg
#         self.detail = detail
#         super().__init__(ex)
#
#
# class NotFoundUserEx(APIException):
#     def __init__(self, username: str = None, ex: Exception = None):
#         super().__init__(
#             status_code=StatusCode.HTTP_409,
#             msg=f"User not found",
#             detail=f"User '{username}' not found",
#             code=f"{StatusCode.HTTP_409}{'1'.zfill(4)}",
#             ex=ex,
#         )
#
#
# class NotAuthorized(APIException):
#     def __init__(self, ex: Exception = None):
#         super().__init__(
#             status_code=StatusCode.HTTP_400,
#             msg=f"Authorization Required",
#             detail="Authorization Required",
#             code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
#             ex=ex,
#         )
#
#
# class TokenExpiredEx(APIException):
#     def __init__(self, ex: Exception = None):
#         super().__init__(
#             status_code=StatusCode.HTTP_400,
#             msg=f"Token Expired. Logged out",
#             detail="Token Expired",
#             code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
#             ex=ex,
#         )
#
#
# class TokenDecodeEx(APIException):
#     def __init__(self, ex: Exception = None):
#         super().__init__(
#             status_code=StatusCode.HTTP_400,
#             msg=f"Invalid token",
#             detail="Token has been compromised.",
#             code=f"{StatusCode.HTTP_400}{'2'.zfill(4)}",
#             ex=ex,
#         )
