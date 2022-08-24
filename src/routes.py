from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from .endpoints.api import HomePage, Signup
from .endpoints.ws import WSGame

routes = [
    Route('/', HomePage),
    Route('/signup', Signup),
    WebSocketRoute('/ws', WSGame),
    Mount('/static', app=StaticFiles(directory='static'))
]
