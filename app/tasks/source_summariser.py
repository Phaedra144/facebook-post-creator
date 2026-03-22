import asyncio
import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.source import Source, SourceItem
from app.services.summariser import summarise_articles

logger = logging.getLogger(__name__)

INTERVAL_SECONDS = 10 * 60  # 10 minutes
BATCH_SIZE = 5


async def summarise_pending_sources() -> None:
    """Summarise the first BATCH_SIZE sources that have no articles_summary but have at least one SourceItem with article_text."""
    loop = asyncio.get_event_loop()
    db: Session = SessionLocal()
    try:
        sources = (
            db.query(Source)
            .filter(Source.articles_summary.is_(None))
            .filter(Source.items.any(SourceItem.article_text.isnot(None)))
            .limit(BATCH_SIZE)
            .all()
        )
        if not sources:
            logger.info("Source summariser: no pending sources.")
            return

        logger.info(f"Source summariser: processing {len(sources)} sources.")
        for source in sources:
            try:
                article_texts = [
                    item.article_text
                    for item in source.items
                    if item.article_text
                ]
                summary = await loop.run_in_executor(None, summarise_articles, article_texts)
                source.articles_summary = summary
                logger.info(f"Summarised source {source.id} ({source.title})")
            except Exception as e:
                logger.warning(f"Failed to summarise source {source.id}: {e}")

        db.commit()
    finally:
        db.close()


async def source_summariser_loop() -> None:
    """Background loop: runs summarise_pending_sources every INTERVAL_SECONDS."""
    while True:
        try:
            await summarise_pending_sources()
        except Exception as e:
            logger.error(f"Source summariser loop error: {e}")
        await asyncio.sleep(INTERVAL_SECONDS)
