from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from config.db import async_session
from src.auth.crud import UserService
from src.auth.validators import password_validator

template = Jinja2Templates(directory='templates')


class HomePage(HTTPEndpoint):
    async def get(self, request: Request):
        return template.TemplateResponse('index.html', {'request': request})


class Signup(HTTPEndpoint):
    async def post(self, request: Request):
        data = await request.json()
        if password_validator(data.get('password1'), data.get('password2')):
            async with async_session() as session:
                async with session.begin():
                    user = UserService(session)
                    new_user = await user.create_user(**data)
                    return JSONResponse({'hello': 'new_user'})
        return JSONResponse({'error': 'password'})
