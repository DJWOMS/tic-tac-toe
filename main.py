from starlette.applications import Starlette

from config.db import engine, Base, async_session
from src.routes import routes


app = Starlette(debug=True, routes=routes)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
    # async with async_session() as session:
    #     await conn.run_sync(Base.metadata.drop_all)
        Base.metadata.bind = engine
        await conn.run_sync(Base.metadata.create_all)
