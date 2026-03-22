import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from sqlalchemy.orm import Session

import app.models  # noqa: F401 — registers all ORM models with Base.metadata
from app.database import Base, engine
from app.migrations.seed_from_js import seed_database
from app.routers import posts
from app.tasks.article_fetcher import article_fetcher_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Seed database with categories and sources from external data
    with Session(engine) as db:
        seed_database(db)

    task = asyncio.create_task(article_fetcher_loop())
    yield
    task.cancel()


app = FastAPI(title="Facebook Post Creator", lifespan=lifespan)
app.include_router(posts.router)


@app.get("/")
async def root():
    return {"message": "Facebook Post Creator API"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
