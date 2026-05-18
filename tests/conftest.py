import sys
import os
os.environ["TESTING"] = "true"
from pathlib import Path
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.dependency import get_db

# Добавляем путь к тестовому модулю
sys.path.insert(0, str(Path(__file__).parent))

# Подменяем redis_client на мок
import redis_mock
import app.redis_client as real_redis_client
real_redis_client.init_redis_pool = redis_mock.init_redis_pool
real_redis_client.close_redis_pool = redis_mock.close_redis_pool
real_redis_client.get_redis = redis_mock.get_redis
real_redis_client.redis_pool = redis_mock.mock_redis_instance  # чтобы не было None

# Теперь можно импортировать приложение
from app.database import Base
from main import app

# Остальная настройка тестов...
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# --- Фикстуры ---
@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client