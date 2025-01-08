import gzip
import logging
from datetime import datetime
from io import BytesIO

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..databases import SessionLocal


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Authentication logic here
        # For example, check if token is valid
        user = request.headers.get("Authorization")
        if user is None:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        # Allow the request to proceed
        response = await call_next(request)
        return response


class AuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Authorization logic here
        user_role = request.state.user_role
        if user_role not in ["admin", "moderator"]:
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        response = await call_next(request)
        return response


class ContextSetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Set some context for the request (e.g., user, request ID)
        request.state.request_id = str(datetime.now().timestamp())  # For example
        response = await call_next(request)
        return response


class SQLAlchemyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Initialize SQLAlchemy session, and attach to request
        request.state.db = SessionLocal  # Assuming you have a SessionLocal() function
        response = await call_next(request)
        request.state.db.close()
        return response


class GZipMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        if "gzip" in request.headers.get("Accept-Encoding", ""):
            # Compress response body with gzip
            buf = BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as f:
                f.write(response.body)
            response.body = buf.getvalue()
            response.headers["Content-Encoding"] = "gzip"
        return response


class LoggingRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logging.info(f"Request path: {request.url.path}")
        response = await call_next(request)
        return response


class TimeHeaderLoggerSetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = datetime.now()
        response = await call_next(request)
        processing_time = datetime.now() - start_time
        response.headers["X-Processing-Time"] = str(processing_time.total_seconds())
        return response
