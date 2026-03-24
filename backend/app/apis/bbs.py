from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional
from app.database import get_db
from app.dependencies.auth import get_current_user, is_author
from app.models.user_model import User
from app.schemas.bbs_schema import BBSCreate
from app.service.bbs_service import BbsService, get_bbs_service
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


PER_PAGE = 10
c_page = 1

# 목록 조회
@router.get("/list", response_class=HTMLResponse)
async def list_bbs(
    request: Request,
    page: int = 1,
    bbs_service: BbsService = Depends(get_bbs_service)
):
    """
    게시글 목록을 조회합니다.
    """
    try:
               
        # 전체 게시글 수
        total = await bbs_service.get_total_count()
       
        # 게시글 목록 조회 (최신순)
        posts = await bbs_service.list_bbs(page=page, per_page=PER_PAGE)
        
        if posts is None:
            raise HTTPException(status_code=500, detail="현재 게시물이 없습니다.")
        
        # 결과를 딕셔너리로 변환
        posts_with_comment_count = [
            {
                'b_idx': post.b_idx,
                'title': post.title,
                'writer': post.username,
                'write_date': post.write_date,
                'hit': post.hit,
                'comment_count': post.comment_count
            }
            for post in posts
        ]
       
        # 페이지 계산 -- 숙제
        total_pages = (total + PER_PAGE - 1) // PER_PAGE
       
        return templates.TemplateResponse(
            "list.html",
            {
                "request": request, # 요청객체
                "posts": posts_with_comment_count, # 목록 배열
                "current_page": page,   # 현재 페이지 값
                "total_pages": total_pages, # 전체 페이지 수
                "total": total, # 전체 게시물 수
                "current_user": None
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 글쓰기 처리
@router.post("/write")
async def write_bbs(bbs_create: BBSCreate, 
                    current_user: User = Depends(get_current_user),
                    bbs_service: BbsService = Depends(get_bbs_service)):
    """
    게시글 작성
    """    
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    # 여기부터는 current_user가 있는 경우만 수행하는 곳이다.
    try:
        bbs = await bbs_service.write_bbs(
            title=bbs_create.title,
            content=bbs_create.content,
            user=current_user
        )
        # 위의 bbs가 뭔가 들어왔다는 것은 저장이 된 상태다.
        if not bbs:
            raise HTTPException(status_code=500, detail="게시물 저장 실패!")
        
        return {"cmd":1, "msg":"저장완료!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/detail/{b_idx}", response_class=HTMLResponse)
async def detail_bbs(request: Request,
                     b_idx: int, 
                     current_user: User = Depends(get_current_user),
                     bbs_service: BbsService = Depends(get_bbs_service)):
        # 사용자가 선택한 게시물 정보를 얻어낸다.
        bbs = await bbs_service.detail_bbs(b_idx)
        
        # 조회수 증가
        bbs.hit = bbs.hit+1
        
        # 현재 게시물의 작성자가 로그인한 사용자와 같은지? 확인
        is_author_flag = current_user and is_author(current_user.id, bbs.user_id)
        
        # 해당 게시물 안에 comments라는 곳에 댓글들이 여러 개 있을 수 있다. 이것을
        # 프론트엔드에서 잘 표현할 수 있도록 List로 변환해야 한다.
        '''
        comments_data = [
            {
                "c_idx": comment.c_idx,
                "content": comment.content,
                "writer": comment.writer,
                "write_date": comment.write_date,
                "is_owner": current_user and current_user.id == comment.user_id
            }
            for comment in bbs.comments
        ]
        '''
        return templates.TemplateResponse(
            "detail.html",
            {
                "request": request,
                "post": bbs,
                "comments":bbs.comments,
                "is_author": is_author_flag, # 현재 게시물의 작성자가 현재 로그인한 사람과 같은지?
                "current_user": current_user
            }
        )