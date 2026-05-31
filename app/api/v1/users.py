from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.util import await_only
from starlette.middleware.sessions import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.service import users as users_service
from app.dependency import get_db, get_current_user
from app.repository import users as users_repository
from app.schemas import UserRequest, UserResponse
from app.tasks import send_welcome_email

router = APIRouter()

@router.post('/users', response_model=UserResponse)
async def create_user(payload: UserRequest,db: AsyncSession= Depends(get_db)):
    return await users_service.create_user(db, payload.login)

@router.get('/users/me', response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_user)):
    return  UserResponse.model_validate(current_user)

@router.post("/users/{user_id}/send-welcome-email")
async def send_welcome_email_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await users_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    task = send_welcome_email.delay(user_id)
    return {"message": "Task enqueued", "task_id": task.id}