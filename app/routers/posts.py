from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dtos.post import PostResponse, PostRunRequest
from app.models.post import Post
from app.services import facebook

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/create", response_model=PostResponse)
async def create_post(request: PostRunRequest, db: Session = Depends(get_db)):
    """Post a message to Facebook and record it in the database."""
    post = Post(status="pending", created_at=datetime.utcnow())
    db.add(post)
    db.flush()  # get post.id before committing

    try:
        fb_post_id = await facebook.post_to_page(message=request.message)
        post.fb_post_id = fb_post_id
        post.status = "posted"
        post.posted_at = datetime.utcnow()
    except Exception as e:
        post.status = "error"
        post.error_message = str(e)

    db.commit()
    db.refresh(post)
    return post


@router.get("/", response_model=list[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).order_by(Post.created_at.desc()).all()


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
