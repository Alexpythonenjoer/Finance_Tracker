from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

async def get_user(db:AsyncSession,login:str) ->User|None:
    result = await db.execute(select(User).where(User.login == login))
    return result.scalar_one_or_none()


async def create_user(db:AsyncSession, login:str) -> User:
    user = User(login=login)
    db.add(user)
    await db.flush()
    return user
