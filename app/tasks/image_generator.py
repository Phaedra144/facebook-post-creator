import asyncio
import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.post import Post
from app.services.cover import CoverGenImageGenerator
from app.services.gemini import GeminiImageGenerator
from app.services.post_creator import extract_dates_from_urls

logger = logging.getLogger(__name__)

INTERVAL_SECONDS = 5 * 60  # 5 minutes
BATCH_SIZE = 1


def get_image_generator():
    """Return the primary image generator with fallback to cover-gen."""
    if settings.gemini_api_key:
        try:
            return GeminiImageGenerator()
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}, falling back to cover-gen")
            return CoverGenImageGenerator()
    return CoverGenImageGenerator()


async def generate_pending_images() -> None:
    """Generate cover images for posts that have text but no image yet.

    Tries Gemini first if API key is configured, falls back to cover-gen on error.
    """
    loop = asyncio.get_event_loop()
    db: Session = SessionLocal()
    try:
        posts = (
            db.query(Post)
            .filter(Post.fb_post_text.isnot(None))
            .filter(Post.image_path.is_(None))
            .limit(BATCH_SIZE)
            .all()
        )
        if not posts:
            logger.info("Image generator: no pending posts.")
            return

        logger.info(f"Image generator: processing {len(posts)} posts.")
        for post in posts:
            try:
                source = post.source
                title = source.title or "" if source else ""
                urls = [item.url for item in source.items] if source else []
                dates = extract_dates_from_urls(urls)
                subtitle = ", ".join(dates) if dates else ""

                # Try primary generator (Gemini if configured, otherwise cover-gen)
                try:
                    primary_gen = get_image_generator()
                    image_path = await loop.run_in_executor(
                        None,
                        lambda: primary_gen.generate(
                            post.id, title, subtitle, post.fb_post_text or ""
                        ),
                    )
                    logger.info(
                        f"Generated image with {primary_gen.__class__.__name__} for post {post.id}"
                    )
                except Exception as primary_err:
                    # If Gemini fails, try cover-gen as fallback
                    logger.warning(f"Primary generator failed for post {post.id}: {primary_err}")
                    if isinstance(primary_gen, GeminiImageGenerator):
                        logger.info(f"Falling back to cover-gen for post {post.id}")
                        fallback_gen = CoverGenImageGenerator()
                        image_path = await loop.run_in_executor(
                            None,
                            lambda: fallback_gen.generate(
                                post.id, title, subtitle, post.fb_post_text or ""
                            ),
                        )
                    else:
                        raise

                post.image_path = str(image_path)
                post.status = "image_ready"
                logger.info(f"Generated cover for post {post.id} at {image_path}")
            except Exception as e:
                logger.warning(f"Cover generation failed for post {post.id}: {e}")

        db.commit()
    finally:
        db.close()


async def image_generator_loop() -> None:
    """Background loop: runs generate_pending_images every INTERVAL_SECONDS."""
    while True:
        try:
            await generate_pending_images()
        except Exception as e:
            logger.error(f"Image generator loop error: {e}")
        await asyncio.sleep(INTERVAL_SECONDS)
