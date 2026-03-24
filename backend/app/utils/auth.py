from datetime import time, timedelta, datetime, timezone
from typing import Optional
from jose import jwt
from app.core.config import config

SECRET_KEY = config.jwt_secret_key
ALGORITHM = config.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = config.jwt_refresh_token_expire_days

# access Token생성 기능
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) 
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # JWT로 변환될 데이터에 만료시간 추가
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# refresh Token생성 기능
def create_refresh_token(data: dict) -> str:
    user_id = data.get("user_id")
    
    expire = datetime.utcnow()+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_payload = {
        "user_id": user_id,
        "exp": expire,
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# access Token 검증 기능 - 유효한 토큰인지?를 검증한다는 것은 decode시키는 것이다.
def verify_access_token(token: str):
    try :
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

# 토큰의 남은 만료시간을 초 단위로 계산해 주는 기능
def get_token_exprire(token: str) -> int:
    try :
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 만료시간만 얻어내자
        exp = payload.get("exp")
        if exp:
            remaining = exp - time.time()
            return max(int(remaining), 1)
    except:
        pass
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60