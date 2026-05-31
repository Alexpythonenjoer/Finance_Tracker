import os

from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, Field, field_validator
from app.api.v1.wallets import router as wallet_router
from app.api.v1.operations import router as operations_router
from app.api.v1.users import router as users_router
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from contextlib import asynccontextmanager
from app.logger import logger
from app.redis_client import init_redis_pool, close_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()
    await init_redis_pool()
    logger.info("Application startup complete.")
    yield

    await close_redis_pool()
    logger.info("Application shutdown complete.")

app = FastAPI(lifespan=lifespan, title="Finance API")

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(wallet_router, prefix='/api/v1', tags=['wallet'])
app.include_router(operations_router,prefix='/api/v1', tags= ['operations'])
app.include_router(users_router, prefix='/api/v1', tags=['users'])
app.mount('/static', StaticFiles(directory='app/static'),name='static')

@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()
    if not os.getenv("TESTING"):
        await init_redis_pool()
    yield

    if not os.getenv("TESTING"):
        await close_redis_pool()