from redis import Redis
from app.core.config import config
from fastapi import FastAPI

redis_config = Redis(
    host=config.redis_host,
    port=config.redis_port,
    db=config.redis_db,
    decode_responses=True, # str로 바로 받기
)

def init_redis(app: FastAPI):
    @app.on_event("startup")  # 프로그램이 시작 시 실행됨
    async def startup_redis_client():
        try:
            redis_config.ping() # 연결 확인함
            print("Redis 준비완료")
        except Exception as e:
            print(f"Redis 문제발생:{e}")
    
    @app.on_event("shutdown")  # 프로그램이 종료시 실행됨
    async def shutdown_redis_client():
        redis_config.close() # 연결 닫기