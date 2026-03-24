from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user_model import User
from app.service.user_service import UserService, get_user_service
from app.utils.auth import verify_access_token

bearer_scheme = HTTPBearer()

# 현재 로그인한 사용자 얻어내기
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        user_service: UserService = Depends(get_user_service)):
    token = credentials.credentials
    
    # 받은 토큰이 로그아웃이 된 토큰인지? 검증 : Redis에 등록된 것인지? 알아야 함!
    
    # 또 받은 토큰이 사용가능한 것인지? 검증
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401,
                            detail="잘 못된 토큰입니다.",
                            headers={"WWW-Authenticate": "Bearer"})
    email = payload.get("email")
    # 지금 얻어낸 email이 DB에 있는지? 재차 검증한다.
    # db연결해서 검증해야 하는데 이거는 user_service를 통해서 하도록 하자!
    # 반환은 User로 받아서 처리하자!
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401,
                            detail="잘 못된 토큰입니다.",
                            headers={"WWW-Authenticate": "Bearer"})
    return user

# 유저 정보 2개를 받아서 같은 유저인지 판단하는 기능
def is_author(current_user: str, author: str) -> bool:
    return current_user == author    