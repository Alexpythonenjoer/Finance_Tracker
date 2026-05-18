from decimal import Decimal

from fastapi import HTTPException
from redis import Redis

from app.dependency import get_redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.enum import CurrencyEnum
from app.models import User
from app.repository import wallets as wallets_repository
from app.schemas import CreateWalletRequest, WalletResponse, TotalBalance
from app.service import exchenge_service

async def get_wallet(db:AsyncSession, current_user: User, redis_client: Redis) -> TotalBalance:
    cache_key = f"user:{current_user.id}:total_balance"
    cached = await redis_client.get(cache_key)
    if cached:
        return TotalBalance(total_balance=Decimal(cached))

    wallets = await wallets_repository.get_all_wallets(db,current_user.id)
    total_balance = Decimal(0)
    for wallet in wallets:
        if wallet.currency == CurrencyEnum.RUB:
            total_balance += wallet.balance
        else:
            exchange_rate = await exchenge_service.get_exchange_rate(wallet.currency, CurrencyEnum.RUB)
            total_balance += exchange_rate * wallet.balance

    await redis_client.setex(cache_key,60,str(total_balance))
    return TotalBalance(total_balance = total_balance)




async def create_wallet(db:AsyncSession,current_user: User, wallet: CreateWalletRequest) -> WalletResponse:

    if await wallets_repository.is_wallet_exist(db,current_user.id,wallet.name):
        raise HTTPException(
            status_code = 400,
            detail = f'Wallet {wallet.name} already exist'
        )

    wallet = await wallets_repository.create_wallet(db, current_user.id, wallet.name, wallet.initial_balance, wallet.currency )
    await db.commit()
    return WalletResponse.model_validate(wallet)

async def get_all_wallets(db:AsyncSession, current_user:User) -> list[WalletResponse]:
    wallets = await wallets_repository.get_all_wallets(db,current_user.id)
    return [WalletResponse.model_validate(wallet) for wallet in wallets]


