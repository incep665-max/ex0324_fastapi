from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env파일의 경로를 준비
DOTENV_PATH = Path(__file__).resolve().parents[1] / ".env"

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8"
    )
    db_name: str
    db_user: str
    db_pwd: str
    db_port: str
    db_loc: str
    
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int
    
    redis_host: str
    redis_port: int
    redis_db: int
    
    @property
    def db_url(self) -> str:
        return f"mysql+aiomysql://{self.db_user}:{self.db_pwd}@{self.db_loc}:{self.db_port}/{self.db_name}"
    
config = Config() # 이때 생성될 때 .env파일을 읽어서 설정값들을 모두 로드함!