from decimal import Decimal
from http.client import responses
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from app.models import User,Wallet
from app.enum import CurrencyEnum, OperationType
@pytest.mark.asyncio
async def test_add_expence_success(db_session: AsyncSession, client: AsyncClient):
    user = User(login = 'test')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name = 'card', balance = 200, user_id = user.id,currency = CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)

    response = await client.post(
        '/api/v1/operations/expense',
        json={
            'wallet_name': 'card',
            'amount': 50,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert response.status_code == 200
    data = response.json()

    assert data['type'] == 'expense'
    assert Decimal(data['amount']) == Decimal('50')
    assert data['currency'] == 'rub'
    assert data['category'] == 'food'
    assert data['wallet_id'] == wallet.id

    await db_session.refresh(wallet)
    assert wallet.balance == Decimal('150')

@pytest.mark.asyncio
async def test_add_expense_negative_amount(db_session: AsyncSession, client: AsyncClient):
    user = User(login='test')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id=user.id, currency = CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)

    response = await client.post(
        '/api/v1/operations/expense',
        json={
            'wallet_name': 'card',
            'amount': -50,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_expence_empty_name(db_session: AsyncSession, client: AsyncClient):
    user = User(login='test')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id=user.id, currency = CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)

    responce = await client.post(
        '/api/v1/operations/expense',
        json={
            'wallet_name': '   ',
            'amount': 50,
            'description': 'food'
        },
        headers = {'Authorization': f'Bearer {user.login}'}
    )
    assert responce.status_code == 422

@pytest.mark.asyncio
async def test_expence_wallet_not_exist(db_session: AsyncSession, client: AsyncClient):
    user = User(login='test')
    db_session.add(user)
    await db_session.commit()

    responce = await client.post(
        '/api/v1/operations/expense',
        json={
            'wallet_name': 'card',
            'amount': 50,
            'description': 'food'
        },
        headers = {'Authorization': f'Bearer {user.login}'}
    )
    assert responce.status_code == 404

@pytest.mark.asyncio
async def test_add_expense_unauthorized(db_session: AsyncSession, client: AsyncClient):

    responce = await client.post(
        '/api/v1/operations/expense',
        json={
            'wallet_name': '   ',
            'amount': 50,
            'description': 'food'
        },
        headers = {'Authorization': f'Bearer not exist'}
    )
    assert responce.status_code == 401

@pytest.mark.asyncio
async def test_add_expence_not_enough_money(db_session: AsyncSession, client: AsyncClient):
    user = User(login = 'test')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name = 'card', balance = 200, user_id = user.id, currency = CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)

    response = await client.post(
        '/api/v1/operations/expense',
        json={
            'wallet_name': 'card',
            'amount': 250,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_add_income_success(db_session: AsyncSession, client: AsyncClient):
    """Успешное добавление дохода: баланс увеличивается, создаётся операция INCOME"""
    user = User(login='test_user')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name='main', balance=Decimal('100'), user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)

    response = await client.post(
        '/api/v1/operations/income',
        json={
            'wallet_name': 'main',
            'amount': 50.0,
            'description': 'salary'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['type'] == OperationType.INCOME
    assert Decimal(data['amount']) == Decimal('50')
    assert data['currency'] == CurrencyEnum.RUB
    assert data['category'] == 'salary'
    assert data['wallet_id'] == wallet.id

    # Проверяем, что баланс кошелька в БД увеличился
    await db_session.refresh(wallet)
    assert wallet.balance == Decimal('150')

@pytest.mark.asyncio
async def test_add_income_negative_amount(db_session: AsyncSession, client: AsyncClient):
    user = User(login='test')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)
    response = await client.post(
        '/api/v1/operations/income',
        json={
            'wallet_name': 'card',
            'amount': -50,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_income_empty_wallet_name(db_session: AsyncSession, client: AsyncClient):
    user = User(login='test')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)

    responce = await client.post(
        '/api/v1/operations/income',
        json={
            'wallet_name': '   ',
            'amount': 50,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert responce.status_code == 422

@pytest.mark.asyncio
async def test_income_wallet_not_exist(db_session: AsyncSession, client: AsyncClient):
    user = User(login = 'test')
    db_session.add(user)
    await db_session.commit()
    responce = await client.post(
        '/api/v1/operations/income',
        json={
            'wallet_name': 'card',
            'amount': 50,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert responce.status_code == 404

@pytest.mark.asyncio
async def test_add_income_unauthorized(db_session: AsyncSession, client: AsyncClient):
    responce = await client.post(
        '/api/v1/operations/income',
        json={
            'wallet_name': 'card',
            'amount': 50,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer not exist'}
    )
    assert responce.status_code == 401

@pytest.mark.asyncio
async def test_add_income_zero_amount(db_session: AsyncSession, client: AsyncClient):
    user = User(login='test')
    db_session.add(user)
    await db_session.flush()
    wallet = Wallet(name='card', balance=200, user_id=user.id, currency=CurrencyEnum.RUB)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(wallet)
    responce = await client.post(
        '/api/v1/operations/income',
        json={
            'wallet_name': 'card',
            'amount': 0,
            'description': 'food'
        },
        headers={'Authorization': f'Bearer {user.login}'}
    )
    assert responce.status_code == 422
