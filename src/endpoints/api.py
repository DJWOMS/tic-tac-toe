import json

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from src.auth.service import UserService, get_session
from src.auth.tokenizator import create_token
from src.auth.validators import password_validator, check_password

template = Jinja2Templates(directory='templates')


class HomePage(HTTPEndpoint):
    async def get(self, request: Request) -> template.TemplateResponse:
        return template.TemplateResponse('index.html', {'request': request})


class Signup(HTTPEndpoint):
    async def post(self, request: Request) -> JSONResponse:
        data = await request.json()
        if password_validator(data.get('password1'), data.get('password2')):
            db_session = await UserService.ainit()
            if not await db_session.user_exist(name=data.get('username'), email=data.get('email')):
                new_user = await db_session.create_user(**data)
                return JSONResponse({'id': new_user.id, 'username': new_user.name})
            return JSONResponse({'error': 'User already exists'}, status_code=400)
        return JSONResponse({'error': 'Invalid password'}, status_code=400)


class Login(HTTPEndpoint):
    async def post(self, request: Request) -> JSONResponse:
        data = await request.json()
        db_session = await UserService.ainit()
        if user := await db_session.get_user(data.get('username')):
            if check_password(data.get('password'), user.password):
                token = create_token(user.id)
                token.update({'username': user.name})
                return JSONResponse(token)
        return JSONResponse({'error': 'Wrong password or username'}, status_code=400)
