from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# 댓글 스키마
class CommentCreate(BaseModel):
    content: str
    writer: str
    
class CommentUpdate(BaseModel):
    content: str
    
class CommentResponse(BaseModel):
    c_idx: int
    content: str
    writer: str
    write_date: datetime
    status: int
    b_idx: int
    
    class Config:
        from_attributes = True # 테이블에 있는 컬럼명과 변수명이 일치하는 값들을 매칭해서 값 가져옴
        
# 게시물 스키마
class BBSListResponse(BaseModel):        
    b_idx: int
    title: str
    write_date: datetime
    write: str
    hit: int
    comment_count: int = 0
    
    class Config:
        from_attributes = True
        
class BBSCreate(BaseModel):
    title: str
    content: str        