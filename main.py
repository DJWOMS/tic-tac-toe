from starlette.applications import Starlette

from src.routes import routes


app = Starlette(debug=True, routes=routes)
