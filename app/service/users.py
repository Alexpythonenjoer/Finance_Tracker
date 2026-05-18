from fastapi import HTTPException
from app.repository import users as users_repository
from app.schemas import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(db:AsyncSession, login:str) -> UserResponse:
    if await users_repository.get_user(db, login):
        raise HTTPException(status_code=400,detail='User already exist')

    user = await users_repository.create_user(db,login)
    await db.commit()
    return UserResponse.model_validate(user)
