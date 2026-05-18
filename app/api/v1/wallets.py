from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependency import get_db, get_current_user, get_redis_client
from app.models import User
from app.service import wallets as wallets_service
from app.schemas import CreateWalletRequest, WalletResponse
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get('/balance')
async def get_balance( db:AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user),
                       redis_client: Redis = Depends(get_redis_client)):
    return await wallets_service.get_wallet(db,current_user,redis_client)


@router.post('/wallets', response_model=WalletResponse)
async def create_wallet(wallet: CreateWalletRequest, db:AsyncSession = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return await wallets_service.create_wallet(db,current_user,wallet)

@router.get('/wallets',response_model=list[WalletResponse])
async def get_all_wallets(db:AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await wallets_service.get_all_wallets(db,current_user)
