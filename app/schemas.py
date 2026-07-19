from datetime import datetime

from pydantic import BaseModel, field_validator


class ArticleCreate(BaseModel):
    source_type: str  # "url" | "note"
    source_url: str | None = None
    raw_content: str | None = None

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        if v not in ("url", "note"):
            raise ValueError('source_type must be "url" or "note"')
        return v


class ArticleResponse(BaseModel):
    id: int
    source_type: str
    source_url: str | None
    raw_content: str | None
    summary: str | None
    status: str
    created_at: datetime
    tags: list[str] = []

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def _tag_names(cls, tags: list) -> list[str]:
        return [tag.name if hasattr(tag, "name") else tag for tag in tags]
