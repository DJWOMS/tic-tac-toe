import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from config.db import engine, Base
from src.middleware import JwtWebSocketsAuthMiddleware
from src.routes import routes


app = Starlette(
    debug=True,
    routes=routes,
    middleware=[
        Middleware(AuthenticationMiddleware, backend=JwtWebSocketsAuthMiddleware()),
        Middleware(CORSMiddleware, allow_origins=['http://127.0.0.1:8000'])
    ]
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=80001)
