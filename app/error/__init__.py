from typing import Optional
from dataclasses import dataclass

unauthorized_value = 401


@dataclass
class AuthBackendException(Exception):
    statusCode: Optional[int] = unauthorized_value
    errorCode: Optional[str] = "UNAUTHORIZED"

    def __init__(self, statusCode=None, errorCode=None):
        if statusCode:
            self.statusCode: int = statusCode
        if errorCode:
            self.errorCode: str = errorCode


### TOD: dataclass 디코레이터 있는데 굳이 __init__ 한 이유?
