"""Backfill published_at on existing SourceItem rows.

Run with:
    python -m app.migrations.backfill_published_at
"""
import logging

import app.models  # noqa: F401 — registers all ORM models with Base.metadata
from app.database import SessionLocal, engine
from app.models.source import SourceItem
from app.utils import extract_dates_from_urls

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def add_column_if_missing() -> None:
    """Add published_at column to source_items if it doesn't exist yet (SQLite safe)."""
    with engine.connect() as conn:
        columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(source_items)")]
        if "published_at" not in columns:
            conn.exec_driver_sql("ALTER TABLE source_items ADD COLUMN published_at DATE")
            conn.commit()
            logger.info("Added published_at column to source_items.")
        else:
            logger.info("Column published_at already exists, skipping ALTER TABLE.")


def backfill() -> None:
    db = SessionLocal()
    try:
        items = db.query(SourceItem).filter(SourceItem.published_at.is_(None)).all()
        logger.info(f"Found {len(items)} SourceItem(s) with no published_at.")

        updated = 0
        for item in items:
            date = extract_dates_from_urls([item.url])[0]
            if date:
                item.published_at = date
                updated += 1

        db.commit()
        logger.info(f"Backfilled {updated} / {len(items)} rows.")
    finally:
        db.close()


if __name__ == "__main__":
    add_column_if_missing()
    backfill()
