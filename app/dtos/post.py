from datetime import datetime

from pydantic import BaseModel


class PostRunRequest(BaseModel):
    message: str = "Hello from Facebook Post Creator!"


class PostResponse(BaseModel):
    id: int
    source_id: int | None
    summary: str | None
    image_url: str | None
    fb_post_id: str | None
    status: str
    error_message: str | None
    created_at: datetime | None
    posted_at: datetime | None

    model_config = {"from_attributes": True}
