import os
from dotenv import load_dotenv
from fastapi import Request, status
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for application access authorization.

    Mandatory to provide:

    @token_fixo: string (Fixed token) (provide in header)
    """

    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        print(f'Received token: {token} ({len(token)})')
        print(f'Request path: {request.url.path}')

        if request.url.path in ["/docs", "/openapi.json"]:
            response = await call_next(request)
            return response

        if token != AUTH_TOKEN:
            print('Token inválido. Necessário autenticação com Bearer Token.')
            print(f'Received token: {token} ({len(token)})')
            print(f'Expected token: {AUTH_TOKEN} ({len(AUTH_TOKEN)})')
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Token inválido. Necessário autenticação com Bearer Token",
                }
            )

        response = await call_next(request)
        return response
