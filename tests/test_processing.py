from app.models import Article
from app.services.llm_provider import LLMProvider
from app.services.processing import process_article
from app.services.scraper import ScrapeError


class FakeProvider(LLMProvider):
    def summarize(self, text: str) -> str:
        return f"summary::{text[:10]}"

    def extract_tags(self, text: str) -> list[str]:
        return ["tag-a", "tag-b"]


def _create_article(db_session_factory, **kwargs) -> int:
    db = db_session_factory()
    article = Article(status="pending", **kwargs)
    db.add(article)
    db.commit()
    article_id = article.id
    db.close()
    return article_id


def test_process_article_note_success(db_session_factory):
    article_id = _create_article(db_session_factory, source_type="note", raw_content="測試內容")

    process_article(article_id, provider=FakeProvider(), session_factory=db_session_factory)

    db = db_session_factory()
    result = db.get(Article, article_id)
    assert result.status == "done"
    assert result.summary == "summary::測試內容"
    assert {tag.name for tag in result.tags} == {"tag-a", "tag-b"}
    db.close()


def test_process_article_url_success(db_session_factory, monkeypatch):
    monkeypatch.setattr(
        "app.services.processing.fetch_and_clean", lambda url: "抓到的網頁內容"
    )
    article_id = _create_article(
        db_session_factory, source_type="url", source_url="https://example.com"
    )

    process_article(article_id, provider=FakeProvider(), session_factory=db_session_factory)

    db = db_session_factory()
    result = db.get(Article, article_id)
    assert result.status == "done"
    assert result.raw_content == "抓到的網頁內容"
    db.close()


def test_process_article_scrape_failure_marks_failed(db_session_factory, monkeypatch):
    def broken_fetch(url):
        raise ScrapeError("boom")

    monkeypatch.setattr("app.services.processing.fetch_and_clean", broken_fetch)
    article_id = _create_article(
        db_session_factory, source_type="url", source_url="https://example.com"
    )

    process_article(article_id, provider=FakeProvider(), session_factory=db_session_factory)

    db = db_session_factory()
    result = db.get(Article, article_id)
    assert result.status == "failed"
    assert result.summary is None
    db.close()


def test_process_article_reuses_existing_tag(db_session_factory):
    first_id = _create_article(db_session_factory, source_type="note", raw_content="第一篇")
    second_id = _create_article(db_session_factory, source_type="note", raw_content="第二篇")

    process_article(first_id, provider=FakeProvider(), session_factory=db_session_factory)
    process_article(second_id, provider=FakeProvider(), session_factory=db_session_factory)

    db = db_session_factory()
    tag_a_count = db.query(Article).count()
    assert tag_a_count == 2
    first = db.get(Article, first_id)
    second = db.get(Article, second_id)
    # 兩篇文章共用同一個 "tag-a" Tag 列,而不是各自產生一筆重複的 tag
    tag_a_ids = {t.id for t in first.tags if t.name == "tag-a"} | {
        t.id for t in second.tags if t.name == "tag-a"
    }
    assert len(tag_a_ids) == 1
    db.close()
