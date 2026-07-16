from fastapi import FastAPI

from app.db import Base, engine
from app.routers import articles

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Knowledge Base API")

app.include_router(articles.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
