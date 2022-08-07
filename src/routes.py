from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from .endpoints import HomePage
from .ws import WSGame

routes = [
    Route('/', HomePage),
    WebSocketRoute('/ws', WSGame),
    Mount('/static', app=StaticFiles(directory='static'))
]
