from datetime import timedelta
from app.core.redis_config import redis_config
from app.utils.auth import REFRESH_TOKEN_EXPIRE_DAYS

TOKEN_BLACKLIST_PREFIX = "blacklist:"
REFRESH_TOKEN_PREFIX = "refresh:"
DEFAULT_TOKEN_EXPIRE = 60*30 # 토큰의 기본 유효시간

class TokenService:
    
    #토큰을 Redis에 'blacklist:'라는 이름을 붙여서 저장하는 기능
    @classmethod
    def blacklist_token(cls, token: str, expires_in: int = DEFAULT_TOKEN_EXPIRE):
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}" 
        redis_config.set(key, "1", ex=expires_in)
        return True
    
    # Redis에 저장된 토큰을 검색하여 삭제하는 기능
    @classmethod
    def blacklist_del_token(cls, token: str):
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        redis_config.delete(key)
        
    # 토큰이 블랙리스트에 있는지? 확인하는 기능
    def is_token_blacklisted(cls, token: str):
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        return redis_config.exists(key) == 1
    
    # Redis에 저장된 블랙리스트들 모두 삭제하는 기능
    @classmethod
    def clear_blacklist(cls):
        for key in redis_config.scan_iter(f"{TOKEN_BLACKLIST_PREFIX}*"):
            redis_config.delete(key)
            
    # Redis에 RefreshToken을 저장하는 기능
    @classmethod
    def store_refresh_token(cls, user_id: str, refresh_token: str):
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"
        
        with redis_config.pipeline() as pipe:
            pipe.sadd(user_key, refresh_token)
            expire_seconds = int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS+1).total_seconds())
            pipe.expire(user_key, expire_seconds)
            pipe.execute()
        return True
    
    # 저장된 RefreshToken이 유효한지 검사하는 기능
    