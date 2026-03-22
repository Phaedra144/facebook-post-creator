from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    title = Column(String, nullable=True)
    articles_summary = Column(Text, nullable=True)

    category = relationship("Category", back_populates="sources")
    items = relationship("SourceItem", back_populates="source", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="source")


class SourceItem(Base):
    __tablename__ = "source_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    text = Column(String, nullable=False)
    url = Column(String, nullable=False)
    article_text = Column(Text, nullable=True)

    source = relationship("Source", back_populates="items")
