from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.db_sync import SyncSessionLocal


async def get_user(db:AsyncSession,login:str) ->User|None:
    result = await db.execute(select(User).where(User.login == login))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db:AsyncSession, login:str) -> User:
    user = User(login=login)
    db.add(user)
    await db.flush()
    return user

def get_user_by_id_sync(user_id: int) -> User | None:
    with SyncSessionLocal() as session:
        return session.query(User).filter(User.id == user_id).first()