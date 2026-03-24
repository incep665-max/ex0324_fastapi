from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy.orm import declarative_base
from app.core.config import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import asyncio
import logging

# 어떤 DB를 연결할 것인지 지정함
engine = create_async_engine(
    config.db_url,
    pool_pre_ping=True # 연결 전 ping시도 후 연결 유지 여부 판단
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

#모델들의 기본객체를 받아온다.
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

logger = logging.getLogger("uvicorn.error")

MAX_RETRIES = 10

# lifespan이벤트 등록 --- main.py에 app = FastAPI(lifespan지정)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # MySQL이 준비될 때까지 재시도하는 반복문
    for attempt in range(1, MAX_RETRIES+1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("DB연결 성공")
            break # 반복문 탈출
        except Exception as e:
            logger.info("DB연결 실패")
            if attempt == MAX_RETRIES:
                logger.error("DB연결 최대 재시도 초과, 프로그램 종료!")
                raise
            await asyncio.sleep(3) #3초 대기
    yield
    # 프로그램 종료될 때 (리소스 닫기)
    await engine.dispose()    