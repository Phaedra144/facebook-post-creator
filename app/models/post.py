from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    summary = Column(Text)
    image_url = Column(String)
    fb_post_id = Column(String)
    status = Column(String, default="pending")  # pending, summarised, image_ready, posted, error
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime)

    source = relationship("Source", back_populates="posts")
