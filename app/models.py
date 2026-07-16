from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, nullable=False)  # "url" | "note"
    source_url = Column(String, nullable=True)
    raw_content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # LLM 處理完才有值
    status = Column(String, nullable=False, default="pending")  # pending|processing|done|failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tags = relationship("Tag", secondary=article_tags, back_populates="articles")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    articles = relationship("Article", secondary=article_tags, back_populates="tags")
