from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import update, or_
from sqlalchemy.future import select

from config.db import async_session
from .validators import get_password_hash
from .models import User


async def get_session():
    async with async_session() as session:
        async with session.begin():
            yield UserService(session)


class UserService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    @classmethod
    async def ainit(cls):
        async with async_session() as session:
            async with session.begin():
                return cls(session)

    async def create_user(self, **kwargs) -> User:
        new_user = User(
            name=kwargs.get('username'),
            password=get_password_hash(kwargs.get('password1')),
            email=kwargs.get('email')
        )
        self.db_session.add(new_user)
        await self.db_session.commit()
        self.db_session.close()
        return new_user

    async def get_all_users(self) -> List[User]:
        query = await self.db_session.execute(select(User).order_by(User.id))
        return query.scalars().all()

    async def get_top_users(self) -> List[User]:
        query = await self.db_session.execute(select(User).order_by(User.win))
        return query.scalars().limit(10).all()

    async def get_user(self, username: str) -> User:
        query = await self.db_session.execute(select(User).where(User.name == username))
        user = query.scalars().first()
        await self.db_session.close()
        return user

    async def filter(self, **kwargs) -> User:
        query = await self.db_session.execute(select(User).filter_by(**kwargs))
        user = query.scalars().first()
        await self.db_session.close()
        return user

    async def user_exist(self, name: str, email: str) -> User:
        query = await self.db_session.execute(select(User.id).filter(
            or_(User.name == name, User.email == email)
        ))
        return query.scalars().first()

    async def update_user(
            self, user_id: int, win: Optional[str], loss: Optional[str], draw: Optional[int]
    ) -> None:
        query = update(User).where(User.id == user_id)
        if win:
            query = query.values(win=win)
        if loss:
            query = query.values(loss=loss)
        if draw:
            query = query.values(draw=draw)
        query.execution_options(synchronize_session="fetch")
        await self.db_session.execute(query)
        await self.db_session.close()
