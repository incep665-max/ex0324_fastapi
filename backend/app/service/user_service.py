from sqlalchemy import select
from fastapi import Depends
from app.database import get_db
from app.models.user_model import User
from app.utils.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # 회원 가입시 호출되는 기능
    
    
    # 이메일을 인자로 받아서 User를 검색하는 기능
    async def get_user_by_email(self, email: str):
        query = (
            select(User)
            .where(User.email == email)
        )
        result = await self.db.execute(query)
        user = result.scalars().one_or_none()
        return user
    
# UserService가 필요할 때 UserService를 반환하는 함수    
def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)