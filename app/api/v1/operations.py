from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from app.service import ai_service
from redis import Redis
from app.repository import wallets as wallets_repository
from app.dependency import get_db, get_current_user, get_redis_client
from app.models import User
from app.service import operations as operations_service
from app.schemas import OperationRequest, OperationResponse, TransferCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter()

@router.post('/operations/income', response_model=OperationResponse)
async def add_income(operation:OperationRequest, db:AsyncSession = Depends(get_db),
               current_user: User = Depends(get_current_user),redis_client: Redis = Depends(get_redis_client)):
    return await operations_service.add_income(db,current_user, operation,redis_client)



@router.post('/operations/expense', response_model=OperationResponse)
async def add_expense(operation: OperationRequest, db:AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user),redis_client: Redis = Depends(get_redis_client)):
    return await operations_service.add_expence(db,current_user,operation,redis_client)

@router.get('/operations', response_model=list[OperationResponse])
async def get_operation_list(
        wallet_id:int | None = Query(None),
        date_from: datetime | None = Query(None),
        date_to: datetime | None = Query(None),
        user: User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
        ):
    return await operations_service.get_operations_list(db,user, wallet_id,date_from,date_to)

@router.post('/operations/transfer',response_model=OperationResponse)
async def create_transfer(
        payload: TransferCreateSchema,
        user: User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db),
        redis_client: Redis = Depends(get_redis_client)

):
    return await operations_service.transfer_between_wallets(db,user.id,payload.from_wallet_id,payload.to_wallet_id,payload.amount, redis_client)


@router.post("/operations/suggest-category")
async def suggest_transaction_category(
        request: OperationRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        redis_client: Redis = Depends(get_redis_client)
):
    wallet = await wallets_repository.is_wallet_exist(
        db, current_user.id, request.wallet_name
    )
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    text_to_analyze = request.category or request.description
    if not text_to_analyze:
        raise HTTPException(status_code=400, detail="No text to analyze")

    cache_key = f"ai_cat:{text_to_analyze.lower().strip()}"
    cached = await redis_client.get(cache_key)
    if cached:
        return {"suggested_category": cached.decode() if isinstance(cached, bytes) else cached}

    suggested = await ai_service.suggest_category(text_to_analyze)
    if not suggested:
        suggested = "Другое"

    await redis_client.setex(cache_key, 86400, suggested)

    return {"suggested_category": suggested}