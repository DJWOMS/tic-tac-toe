from starlette.applications import Starlette

from config.db import engine, Base
from src.routes import routes


app = Starlette(debug=True, routes=routes)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
