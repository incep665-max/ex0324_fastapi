from datetime import timedelta

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user_model import User
from app.schemas.auth_schema import LoginRequest
from app.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, create_refresh_token
from app.utils.security import verify_password
from app.service.token_service import TokenService

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    # 이메일과 비밀번호로 회원 조회
    async def authenticate_user(self, login_data:LoginRequest):
        query = (
            select(User)
            .where(User.email == login_data.email)
        )
        result = await self.db.execute(query)
        user = result.scalars().one_or_none()
        if not user:
            return None
        # 여기에 제어가 오게되면 user가 있는 상태고, user가 가지고 있는
        # 암호화된 비밀번호와 인자로 넘어온 login_data에 있는 비밀번호가 같은 것인지? 확인받아야 한다.
        if not verify_password(login_data.password, user.pwd):
            return None
        return user

    def create_user_token(self, user: User):
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
        expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_token = create_access_token(data=token_data, expires_delta=expire)
        # refresh토큰 생성
        refresh_token = create_refresh_token(token_data)
        
        TokenService.store_refresh_token(user.id, refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    # access token이 만료되어 로그인상태를 유지하기 위해 refresh token을 전달해서
    # 새로운 access token을 발급받는 기능
    

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)