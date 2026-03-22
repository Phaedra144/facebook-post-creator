import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy.orm import Session

import app.models  # noqa: F401 — registers all ORM models with Base.metadata
from app.database import Base, engine
from app.migrations.seed_from_js import seed_database
from app.routers import posts
from app.tasks.article_fetcher import article_fetcher_loop
from app.tasks.source_summariser import source_summariser_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Seed database with categories and sources from external data
    with Session(engine) as db:
        seed_database(db)

    task = asyncio.create_task(article_fetcher_loop())
    summariser_task = asyncio.create_task(source_summariser_loop())
    yield
    task.cancel()
    summariser_task.cancel()


app = FastAPI(title="Facebook Post Creator", lifespan=lifespan)
app.include_router(posts.router)


@app.get("/")
async def root():
    return {"message": "Facebook Post Creator API"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
