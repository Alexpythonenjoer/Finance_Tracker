import os
from redis.asyncio import Redis, ConnectionPool

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

TESTING = os.getenv("TESTING", "").lower() == "true"

class MockRedis:
    async def get(self, key):
        return None
    async def setex(self, key, time, value):
        pass
    async def delete(self, *keys):
        pass
    async def ping(self):
        return True
    async def close(self):
        pass

if TESTING:

    _mock_redis = MockRedis()
    async def init_redis_pool():
        print("Redis disabled for testing, using mock")
        return _mock_redis
    async def close_redis_pool():
        pass
    def get_redis():
        return _mock_redis
else:

    redis_pool: ConnectionPool | None = None

    async def init_redis_pool() -> Redis:
        global redis_pool
        redis_pool = ConnectionPool.from_url(REDIS_URL, max_connections=20, decode_responses=True)
        print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return Redis(connection_pool=redis_pool)

    async def close_redis_pool():
        if redis_pool:
            await redis_pool.disconnect()
            print("Redis connection pool closed.")

    def get_redis() -> Redis:
        if redis_pool is None:
            raise RuntimeError("Redis connection pool not initialized. Call init_redis_pool() first.")
        return Redis(connection_pool=redis_pool)