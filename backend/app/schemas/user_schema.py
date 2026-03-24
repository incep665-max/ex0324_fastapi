from datetime import datetime
from pydantic import BaseModel, Field

# User관련 베이스 모델 정의
class UserBase(BaseModel):
    username: str
    email: str
    
# 베이스 모델에는 공통 속성들만 정의해서 자식들이 상속받아
# 중복되는 것을 해결한다.

class UserCreate(UserBase):
    pwd: str = Field(..., min_length=4, max_length=20)
    
class UserResponse(UserBase):
    id: int
    status: int 
    
    #model_config = {
    #    "from_attributes": True
    #}
    class Config:
        from_attributes = True