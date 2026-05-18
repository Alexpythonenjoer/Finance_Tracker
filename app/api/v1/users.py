from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.util import await_only
from starlette.middleware.sessions import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.service import users as users_service
from app.dependency import get_db, get_current_user
from app.schemas import UserRequest, UserResponse

router = APIRouter()

@router.post('/users', response_model=UserResponse)
async def create_user(payload: UserRequest,db: AsyncSession= Depends(get_db)):
    return await users_service.create_user(db, payload.login)

@router.get('/users/me', response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_user)):
    return  UserResponse.model_validate(current_user)
