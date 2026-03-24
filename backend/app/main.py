from fastapi import FastAPI
from app.database import lifespan
from app.apis import bbs, auth

app = FastAPI(lifespan=lifespan)

# 라우터 등록
app.include_router(bbs.router, prefix="/bbs")
app.include_router(auth.router, prefix="/auth")


@app.get("/")
async def root():
    return {"message":"FastAPI start"}
