from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class BBS(Base):
    __tablename__ = "bbs"
    
    b_idx = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    write_date = Column(DateTime, nullable=False, default=datetime.now)
    hit = Column(Integer, default=0)
    status = Column(Integer, default=0)
    
    #관계설정 ******
    author = relationship("User", back_populates="bbs_posts", lazy="select")
    comments = relationship("Comment", back_populates="bbs", 
                            cascade="all, delete-orphan", lazy="select")
    # Comment : 연결할 자식 모델클래스 지정
    # back_populates="bbs" : 양방향 관계를 명시적으로 설정 ( 앞서 지정한 자식 모델클래스의 bbs라는 변수를 지칭 )
    # cascade="all, delete-orphan" : 부모(BBS)객체에 대한 변경사항이 자식(Comment)에 연쇄적으로 적용되게 함
    # lazy="select" : 기본값 - 관계 데이터 로딩 전략 지정( select쿼리로 lazy(지연)로드로 한다 )
    
    # property들 추가
    @property
    def writer(self): # 작성자 이름을 반환한다.
        return self.author.username if self.author else "Unknown"


class Comment(Base):
    __tablename__ = "comment"
    
    c_idx = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    b_idx = Column(Integer, ForeignKey("bbs.b_idx"), nullable=False)
    write_date = Column(DateTime, nullable=False, default=datetime.now)
    status = Column(Integer, default=0)    
    
    # 관계설정
    bbs = relationship("BBS", back_populates="comments", lazy="select")
    author = relationship("User", back_populates="comments", lazy="select")
    
    @property
    def writer(self): # 작성자 이름을 반환한다.
        return self.author.username if self.author else "Unknown"