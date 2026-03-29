import asyncio
import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.post import Post
from app.models.source import Source, SourceItem
from app.services.post_creator import create_facebook_post_text

logger = logging.getLogger(__name__)

INTERVAL_SECONDS = 5 * 60  # 5 minutes
BATCH_SIZE = 3


async def create_pending_posts() -> None:
    """Create facebook post texts for sources that have a summary but no post yet."""
    loop = asyncio.get_event_loop()
    db: Session = SessionLocal()
    try:
        sources = (
            db.query(Source)
            .outerjoin(Source.items)
            .filter(Source.articles_summary.isnot(None))
            .filter(~Source.posts.any())
            .group_by(Source.id)
            .order_by(func.min(SourceItem.published_at).asc())
            .limit(BATCH_SIZE)
            .all()
        )
        if not sources:
            logger.info("Post creator: no pending sources.")
            return

        logger.info(f"Post creator: processing {len(sources)} sources.")
        for source in sources:
            try:
                urls = [item.url for item in source.items]
                dates = list(dict.fromkeys(item.published_at for item in source.items if item.published_at))
                fb_post_text = await loop.run_in_executor(
                    None,
                    create_facebook_post_text,
                    source.title or "",
                    source.articles_summary,
                    source.category.name if source.category else "",
                    urls,
                    dates,
                )
                post = Post(source_id=source.id, fb_post_text=fb_post_text, status="pending")
                db.add(post)
                logger.info(f"Created post for source {source.id} ({source.title})")
            except Exception as e:
                logger.warning(f"Failed to create post for source {source.id}: {e}")

        db.commit()
    finally:
        db.close()


async def post_creator_loop() -> None:
    """Background loop: runs create_pending_posts every INTERVAL_SECONDS."""
    while True:
        try:
            await create_pending_posts()
        except Exception as e:
            logger.error(f"Post creator loop error: {e}")
        await asyncio.sleep(INTERVAL_SECONDS)
