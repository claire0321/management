# from fastapi import Request
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import JSONResponse
#
# from ..authorization.login import Token
#
#
# class AuthMiddleWare(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         if request.url.path in ["/docs", "/openapi.json"]:
#             return await call_next(request)
#
#         # 1. 토큰을 가져온다 (request.headers['Authorization']
#         auth_header = request.headers.get("Authorization")
#         print("auth_header:", auth_header)
#         # Bearer {TOKEN}
#         # 1-1 토큰이 없으면 status 403으로 반환
#         if not auth_header or not auth_header.startswith("Bearer"):
#             return JSONResponse(status_code=403, content={"status": 403})
#
#         token = auth_header.split(" ")[1]
#         print(token)
#
#         # 2. 토큰 검증
#         user_info = Token.verify_token(token)
#         print("user_info:", user_info)
#
#         # 2-1. 검증 실패 status 403 변환
#         if user_info is None:
#             return JSONResponse(status_code=403, content={"status": 403})
#
#         # 3. 유저 정보를 request 안에 user라는 키에 넣어준다
#         request.state.user = user_info
#
#         # 검증
#         # 1. route에서 request.status.user를 해서 값 가져옴
#         # 2. 로그인을 안한경우 status 403
#         response = await call_next(request)
#         return response
