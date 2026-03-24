
from app.core.jinja2 import templates
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.service.auth_service import AuthService, get_auth_service
from app.service.token_service import TokenService
from app.utils.auth import get_token_exprire


router = APIRouter()
bearer_scheme = HTTPBearer()

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login",
             response_model=TokenResponse,
             summary="로그인",
             description="사용자 이메일과 비밀번호로 로그인합니다.",
             responses={
                 401:{
                     "description":"이메일이 존재하지 않습니다.",
                     "content":{
                         "application/json":{
                             "example": {
                                 "detail":"입력한 이메일이 없어요"
                             }
                         }
                     }
                 }
             })
async def login(login_data: LoginRequest,auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.authenticate_user(login_data)
    if not user: # user정보가 없다면
        raise HTTPException(
            staus_code=401,
            detail="인증 실패",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = auth_service.create_user_token(user)
    return token

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    # 헤더에서 토큰 추출(가져온다.)
    token = credentials.credentials
    
    # 현재 토큰의 만료시간 계산
    token_expire = get_token_exprire(token)
    
    # 토큰을 더 이상 사용할 수 없도록 Redis에 블랙리스트로 등록
    TokenService.blacklist_token(token, token_expire)
    
    return {"cmd":1, "msg":"로그아웃 되었습니다."}