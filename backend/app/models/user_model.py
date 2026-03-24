from sqlalchemy import Column, DateTime, Integer, String, func
from app.database import Base
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING: # 순환 import를 피하기 위한 조건문
    from .bbs_model import BBS, Comment # 순환 참조 방지를 위해 타입 힌트로만 사용함

class User(Base):
    __tablename__ = "users"
    __allow_unmapped__ = True # 타입 힌트가 완전히 컬럼의 형태가 아니어도 매핑을 허용
    
    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(120), unique=True, index=True)
    username: str = Column(String(50))
    pwd: str = Column(String(200), nullable=False)
    status: int = Column(Integer, default=0)
    
    # 관계설정
    bbs_posts = relationship( # User <-> BBS(게시글) , 1:N관계(해당 사용자가 쓴 글 목록 설정)
        "BBS", # 연결한 대상 모델
        back_populates="author", # BBS쪽의 author와의 양방향 관계로 연결
        foreign_keys="BBS.user_id", # BBS쪽의 user_id가 외래키로 사용됨
        lazy="select" # Async환경에서 MissingGreenlet 이슈의 원인이 될 수 있다고 함
    )
    
    comments = relationship(
        "Comment",
        back_populates="author",
        foreign_keys="Comment.user_id", 
        lazy="select"
    )