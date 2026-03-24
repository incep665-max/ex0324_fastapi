from app.models.user_model import User
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import func, select

from app.database import get_db
from app.models.bbs_model import BBS, Comment
from sqlalchemy.orm import selectinload


class BbsService:
    # 초기자(생성자)
    def __init__(self, db: AsyncSession):
        self.db = db # 멤버변수 db에 인자로 넘어온 지역변수 db의 값을 저장함
        
    async def get_total_count(self):
        stmt = select(func.count(BBS.b_idx)).where(BBS.status == 0)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())
    
    def _commnet_count_sq(self):
        return (
            select(
                Comment.b_idx.label("b_idx"),
                func.count(Comment.c_idx).label("comment_count"),
            )
            .where(Comment.status == 0)
            .group_by(Comment.b_idx)
            .subquery()
        )
    
    # 목록 조회 - page:현재페이지값, per_page:한페이지당 보여질 게시물의 수
    async def list_bbs(self, page: int=1, per_page: int=10):
        try:
            page = max(page, 1)
            per_page = min(max(per_page, 1), 100)
            skip = (page-1)*per_page
            
            comment_count_query = self._commnet_count_sq()
            stmt = (
                select(
                    BBS.b_idx,
                    BBS.title,
                    User.username, # 요~~기 추가
                    BBS.write_date,
                    BBS.hit,
                    func.coalesce(comment_count_query.c.comment_count, 0).label("comment_count")
                )
                .select_from(BBS)
                .join(User, BBS.user_id == User.id) # User테이블과 조인
                .outerjoin(comment_count_query, 
                           comment_count_query.c.b_idx == BBS.b_idx)
                .where(BBS.status == 0)
                .order_by(BBS.b_idx.desc())
                .offset(skip) # 현재페이지 값에 의해 skip의 수만큼 제외
                .limit(per_page) # skip된 이 후 per_page가 기억하는 수만큼 가져온다.
            )
            # subquery()를 반드시 호출해야 c속성이 생긴다. select()만 반환하면 c속성이 없어서
            # AttributeError가 발생하므로 붙여야 한다.
            
            result = await self.db.execute(stmt)
            rows = result.all() 
            return rows
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # 글쓰기 처리
    async def write_bbs(self, title: str, content: str, user: User):
        new_bbs = BBS(
            title = title,
            content = content,
            user_id = user.id
        )
        self.db.add(new_bbs) # db세션에 등록
        await self.db.commit() # db에 적용
        await self.db.refresh(new_bbs) # new_db의 내용이 db에 적용된 내용과 동일하게 만듬
        
        return new_bbs # 호출한 곳으로 반환 - apis/bbs.py안에 있는 write_bbs함수로 돌려준다.
    
    # 게시글 상세보기 기능
    async def detail_bbs(self, b_idx: int):
        query = (
            select(BBS)
            .where(BBS.b_idx == b_idx, BBS.status == 0)
            .options(
                selectinload(BBS.author), # 글쓴이 정보: User
                selectinload(BBS.comments) # 댓글 목록
                .selectinload(Comment.author) # 댓글 각각의 작성자 정보
            ) # 즉, 게시글만 가져오는 것이 아니라 관계된 User와 Comment들이 모두 로드된다.
        )
        
        result = await self.db.execute(query)
        bbs = result.scalars().one_or_none()
        if not bbs:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
        # 삭제된 댓글 제외
        bbs.comments = [c for c in bbs.comments if c.status == 0]
        
        return bbs
        
def get_bbs_service(db: AsyncSession = Depends(get_db)):
    return BbsService(db)