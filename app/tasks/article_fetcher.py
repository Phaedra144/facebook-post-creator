import asyncio
import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.source import SourceItem
from app.services.article import fetch_article

logger = logging.getLogger(__name__)

INTERVAL_SECONDS = 20 * 60  # 20 minutes
BATCH_SIZE = 10


async def fetch_pending_articles() -> None:
    """Fetch article text for the first BATCH_SIZE SourceItems with no article_text."""
    loop = asyncio.get_event_loop()
    db: Session = SessionLocal()
    try:
        items = (
            db.query(SourceItem)
            .filter(SourceItem.article_text.is_(None))
            .limit(BATCH_SIZE)
            .all()
        )
        if not items:
            logger.info("Article fetcher: no pending items.")
            return

        logger.info(f"Article fetcher: processing {len(items)} items.")
        for item in items:
            try:
                fetched = await loop.run_in_executor(None, fetch_article, item.url)
                item.article_text = fetched["text"]
                logger.info(f"Fetched article for SourceItem {item.id}: {item.url}")
            except Exception as e:
                logger.warning(f"Failed to fetch article for SourceItem {item.id} ({item.url}): {e}")

        db.commit()
    finally:
        db.close()


async def article_fetcher_loop() -> None:
    """Background loop: runs fetch_pending_articles every INTERVAL_SECONDS."""
    while True:
        try:
            await fetch_pending_articles()
        except Exception as e:
            logger.error(f"Article fetcher loop error: {e}")
        await asyncio.sleep(INTERVAL_SECONDS)
