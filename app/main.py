from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import app.models  # noqa: F401 — registers all ORM models with Base.metadata
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Facebook Post Creator", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Facebook Post Creator API"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
