from collections.abc import Callable

import httpx
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Article, Tag
from app.services.llm_provider import LLMProvider, OllamaProvider
from app.services.scraper import ScrapeError, fetch_and_clean

_default_provider: LLMProvider = OllamaProvider()


def process_article(
    article_id: int,
    provider: LLMProvider | None = None,
    session_factory: Callable[[], Session] = SessionLocal,
) -> None:
    """背景任務進入點:抓取內容(若為 url)→ 呼叫 LLM 摘要/標籤 → 更新 status。"""
    provider = provider or _default_provider
    db = session_factory()
    try:
        article = db.get(Article, article_id)
        if article is None:
            return

        article.status = "processing"
        db.commit()

        try:
            if article.source_type == "url":
                article.raw_content = fetch_and_clean(article.source_url)

            article.summary = provider.summarize(article.raw_content)
            article.tags = _resolve_tags(db, provider.extract_tags(article.raw_content))
            article.status = "done"
        except (ScrapeError, httpx.HTTPError):
            article.status = "failed"

        db.commit()
    finally:
        db.close()


def _resolve_tags(db: Session, names: list[str]) -> list[Tag]:
    tags = []
    for name in names:
        tag = db.query(Tag).filter_by(name=name).first()
        if tag is None:
            tag = Tag(name=name)
        tags.append(tag)
    return tags
