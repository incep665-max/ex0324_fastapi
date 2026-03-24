from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 암호화 - 회원 가입 시 사용함
def hash_password(password: str):
    return pwd_context.hash(password)

# 비밀번호 검증 - 로그인 시 사용함
def verify_password(plain_pwd: str, hashed_pwd: str):
    return pwd_context.verify(plain_pwd, hashed_pwd)