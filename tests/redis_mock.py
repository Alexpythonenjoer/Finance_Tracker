# tests/redis_mock.py
from unittest.mock import AsyncMock

class MockRedis:
    def __init__(self):
        self.connection_kwargs = {}
        self.get = AsyncMock(return_value=None)
        self.setex = AsyncMock()
        self.delete = AsyncMock()
        self.ping = AsyncMock(return_value=True)

    async def close(self):
        pass

mock_redis_instance = MockRedis()

async def init_redis_pool():
    print("Test Redis initialized (mock)")
    return mock_redis_instance

async def close_redis_pool():
    print("Test Redis closed (mock)")

def get_redis():
    return mock_redis_instance
