from decimal import Decimal

from fastapi import HTTPException, Depends
from redis import Redis
from sqlalchemy.util import await_only

from app.database import SessionLocal
from app.dependency import get_current_user, get_db
from app.enum import OperationType
from app.models import User
from app.repository import wallets as wallets_repository
from app.repository import operations as operations_repository
from app.schemas import OperationRequest, OperationResponse
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.service.exchenge_service import get_exchange_rate


async def add_income(db:AsyncSession, current_user: User,operation:OperationRequest,redis_client: Redis)->OperationResponse:

    if not await wallets_repository.is_wallet_exist(db,current_user.id,operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f'Wallet {operation.wallet_name} not found'
        )

    wallet = await wallets_repository.add_income(db,current_user.id,operation.wallet_name,operation.amount)
    operation = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type= OperationType.INCOME,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.get_category()
    )
    await db.commit()
    cache_key = f"user:{current_user.id}:total_balance"
    await redis_client.delete(cache_key)
    return OperationResponse.model_validate(operation)


async def add_expence(db:AsyncSession,current_user: User,operation: OperationRequest, redis_client: Redis)->OperationResponse:

    if not await wallets_repository.is_wallet_exist(db, current_user.id,operation.wallet_name):
        raise HTTPException(
            status_code=404,
            detail=f'Wallet {operation.wallet_name} not found'
        )

    wallet = await wallets_repository.get_wallet_balance_by_name(db,current_user.id,operation.wallet_name)


    if wallet.balance < operation.amount:
        raise HTTPException(
            status_code = 400,
            detail = f'Insufficient found: Available: {wallet.balance}'

        )
    wallet = await wallets_repository.add_expense(db,current_user.id,operation.wallet_name,operation.amount)
    operation = await operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.EXPENSE,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.get_category()
    )
    await db.commit()
    cache_key = f"user:{current_user.id}:total_balance"
    await redis_client.delete(cache_key)
    return OperationResponse.model_validate(operation)


async def get_operations_list(
        db:AsyncSession,
        current_user: User,
        wallet_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        ) -> list[OperationResponse]:
    if wallet_id:
        wallet = await wallets_repository.get_wallet_by_id(db, current_user.id, wallet_id)
        if not wallet:
            raise HTTPException(
                status_code=404,
                detail=f'Wallet{wallet_id} not found'
            )
        wallets_ids = [wallet.id]
    else:
        wallets = await wallets_repository.get_all_wallets(db,current_user.id)
        wallets_ids = [w.id for w in wallets]
    operations = await operations_repository.get_operation_list(
        db,
        wallets_ids,
        date_from,
        date_to
    )
    result = []
    for operation in operations:
        result.append(OperationResponse.model_validate(operation))
    return result

async def transfer_between_wallets(db:AsyncSession, user_id: int,
                             from_wallet_id:int,
                             to_wallet_id:int,
                             amount:Decimal,
                             redis_client: Redis) -> OperationResponse:
    from_wallet = await wallets_repository.get_wallet_by_id(db, user_id,from_wallet_id)
    to_wallet = await wallets_repository.get_wallet_by_id(db, user_id, to_wallet_id)
    if not from_wallet or not to_wallet:
        raise HTTPException(status_code=404, detail='Wallet not found')
    if from_wallet.balance < amount:
        raise HTTPException(
            status_code=400,
            detail=f'Not enough money {from_wallet.balance} {from_wallet.currency}'
        )
    target_amount = amount
    exchange_rate = 1.0
    if from_wallet.currency != to_wallet.currency:
        exchange_rate = await  get_exchange_rate(from_wallet.currency,to_wallet.currency)
        target_amount = round(amount * exchange_rate,2 )

    from_wallet.balance = round(from_wallet.balance - amount, 2)
    to_wallet.balance = round(to_wallet.balance + target_amount, 2)
    operation = await operations_repository.create_operation(
        db= db,
        wallet_id=from_wallet_id,
        type=OperationType.TRANSFER,
        amount=target_amount,
        currency=to_wallet.currency,
        category='перевод'
    )
    db.add(from_wallet)
    db.add(to_wallet)
    db.add(operation)
    await db.commit()
    cache_key = f"user:{user_id}:total_balance"
    await redis_client.delete(cache_key)
    return OperationResponse.model_validate(operation)






















