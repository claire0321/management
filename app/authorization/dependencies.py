from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from . import verify_token
from app.error.exceptions import InvalidToken


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = verify_token(token)

        if not token_data:
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")
