class StatusCode:
    HTTP_500 = 500
    HTTP_400 = 400
    HTTP_401 = 401
    HTTP_403 = 403
    HTTP_404 = 404
    HTTP_405 = 405
    HTTP_409 = 409


class APIException(Exception):
    status_code: int
    code: str
    msg: str
    detail: str

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_500,
        code: str = "000000",
        msg: str = None,
        detail: str = None,
        ex: Exception = None,
    ):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.detail = detail
        super().__init__(ex)


class NotFoundUserEx(APIException):
    def __init__(self, username: str = None, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_409,
            msg=f"User not found",
            detail=f"User '{username}' not found",
            code=f"{StatusCode.HTTP_409}{'1'.zfill(4)}",
            ex=ex,
        )


class NotAuthorized(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"Authorization Required",
            detail="Authorization Required",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )


class TokenExpiredEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"Token Expired. Logged out",
            detail="Token Expired",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )


class TokenDecodeEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"Invalid token",
            detail="Token has been compromised.",
            code=f"{StatusCode.HTTP_400}{'2'.zfill(4)}",
            ex=ex,
        )
