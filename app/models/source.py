from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.category import Category


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    text = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)

    category = relationship("Category", back_populates="sources")
    posts = relationship("Post", back_populates="source")
