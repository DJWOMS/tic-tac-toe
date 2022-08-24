from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.future import select

from .validators import get_password_hash
from .models import User


class UserCRUD:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, **kwargs):
        new_user = User(
            name=kwargs.get('username'),
            password=get_password_hash(kwargs.get('password1')),
            email=kwargs.get('email')
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def get_all_users(self) -> List[User]:
        q = await self.db_session.execute(select(User).order_by(User.id))
        return q.scalars().all()

    async def get_top_users(self) -> List[User]:
        q = await self.db_session.execute(select(User).order_by(User.win))
        return q.scalars().all()

    async def update_user(
            self, user_id: int, win: Optional[str], loss: Optional[str], draw: Optional[int]
    ):
        q = update(User).where(User.id == user_id)
        if win:
            q = q.values(win=win)
        if loss:
            q = q.values(loss=loss)
        if draw:
            q = q.values(draw=draw)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
