from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.enum import CurrencyEnum


class OperationRequest(BaseModel):
    wallet_name:str = Field(..., max_length=127)
    amount: Decimal
    category: str | None = Field(None, max_length=250)
    description : str | None=Field(None, max_length=250)

    @field_validator('amount')
    def amount_must_be_positive(cls, v: Decimal ) -> Decimal:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v:str)->str:
        v = v.strip()
        if not v:
            raise ValueError('Wallet name cant be empty')
        return v

    def get_category(self) -> str | None:
        return self.category or self.description

class CreateWalletRequest(BaseModel):
    name:str = Field(..., max_length=127)
    initial_balance: Decimal = 0
    currency: CurrencyEnum = CurrencyEnum.RUB

    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Wallet name cant be empty')
        return v

    @field_validator('initial_balance')
    def balance_must_be_positive(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError('Balance must be positive')
        return v

class UserRequest(BaseModel):
    login: str = Field(...,max_length=127)

class UserResponse(UserRequest):
    model_config = {'from_attributes': True}
    id: int

class WalletResponse(BaseModel):
    model_config = {'from_attributes': True}
    id:int
    name:str
    balance: Decimal
    currency: CurrencyEnum

class OperationResponse(BaseModel):
    model_config = {'from_attributes': True}
    id: int
    wallet_id: int
    type: str
    amount: Decimal
    currency: CurrencyEnum
    category: str|None
    subcategory: str|None
    created_at: datetime

class TransferCreateSchema(BaseModel):
    from_wallet_id: int
    to_wallet_id:int
    amount: Decimal

    @field_validator('to_wallet_id')
    @classmethod
    def wallets_must_differ(cls, v:int, info) -> int:
        if 'from_wallet_id' in info.data and v == info.data['from_wallet_id']:
            raise ValueError('Same wallets ids!')
        return v
    @field_validator('amount')
    @classmethod
    def amount_gt_zero(cls, v:Decimal) -> Decimal:
        if v < 0:
            raise ValueError('Amount cannot be negative!')
        return v

class TotalBalance(BaseModel):
    total_balance:Decimal