from fastapi import HTTPException
from fastapi.params import Depends
from app.database import SessionLocal
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from app.repository import users as users_repository
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from app.redis_client import get_redis

security = HTTPBearer()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                     db:AsyncSession = Depends(get_db)) -> User:
    login = credentials.credentials
    user = await users_repository.get_user(db, login)
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return user

async def get_redis_client() -> Redis:
    return get_redis()