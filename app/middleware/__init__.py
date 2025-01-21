from fastapi import FastAPI

from app.error.error_handler import (
    auth_error_handler,
    invalid_token_exception_handler,
    role_not_found_exception_handler,
)
from app.error.exceptions import AuthBackendException, InvalidToken, RoleNotFound
from app.middleware import auth_middleware


def init_middleware(app: FastAPI):
    exception_handlers = {
        AuthBackendException: auth_error_handler,
        InvalidToken: invalid_token_exception_handler,
        RoleNotFound: role_not_found_exception_handler,
    }

    app.add_middleware(auth_middleware.AuthorizationMiddleware)
    app.add_middleware(auth_middleware.AuthenticationMiddleware, on_error=exception_handlers)
    # app.add_middleware(CatchExceptionMiddleware, on_error=UnexpectedErrors)


#
# logging.basicConfig(level=logging.ERROR)
# logger = logging.getLogger(__name__)
#
#
# class CatchExceptionMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, on_error=None):
#         super().__init__(app)
#         self.on_error = on_error
#
#     async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
#         try:
#             response = await call_next(request)
#             return response
#         except Exception as e:
#             logger.error("Unhandled exception occurred", exc_info=e)
#             print_exception(e)
#             return Response("Unexpected error", status_code=500)
