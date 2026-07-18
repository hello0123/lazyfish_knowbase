from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Article
from app.schemas import ArticleCreate, ArticleResponse
from app.services.processing import process_article

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleResponse, status_code=201)
def create_article(
    payload: ArticleCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Article:
    if payload.source_type == "url" and not payload.source_url:
        raise HTTPException(400, "source_url is required when source_type is 'url'")
    if payload.source_type == "note" and not payload.raw_content:
        raise HTTPException(400, "raw_content is required when source_type is 'note'")

    article = Article(
        source_type=payload.source_type,
        source_url=payload.source_url,
        raw_content=payload.raw_content,
        status="pending",
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    background_tasks.add_task(process_article, article.id)
    return article


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)) -> Article:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(404, "Article not found")
    return article
