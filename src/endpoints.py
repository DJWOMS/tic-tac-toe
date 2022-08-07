from starlette.endpoints import HTTPEndpoint
from starlette.templating import Jinja2Templates

template = Jinja2Templates(directory='templates')


class HomePage(HTTPEndpoint):
    async def get(self, request):
        return template.TemplateResponse('index.html', {'request': request})
