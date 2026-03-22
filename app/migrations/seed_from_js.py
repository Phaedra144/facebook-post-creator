"""
Seed script to populate categories and sources from JavaScript data.
Runs on app startup (idempotent — uses INSERT OR IGNORE).
"""

import json
import logging
import re
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.models import Category, Source, SourceItem

logger = logging.getLogger(__name__)

# External URL to fetch sources from
NERLIST_DB_URL = "https://nerlist.hu/js/db.js"


def fetch_nerlist_data() -> dict[str, Any]:
    """
    Fetch and parse data from the external JavaScript file.
    Converts JavaScript object notation to valid JSON for parsing.
    Returns the parsed dict.
    """
    try:
        response = httpx.get(NERLIST_DB_URL, timeout=10)
        response.raise_for_status()

        # Get content and ensure proper encoding
        content = response.text

        # Try to find and extract JSON object from various patterns
        patterns = [
            "var htmlData = ",
            "var htmlData=",
            "htmlData = ",
            "htmlData=",
        ]

        json_start = -1
        for pattern in patterns:
            pos = content.find(pattern)
            if pos != -1:
                json_start = pos + len(pattern)
                break

        if json_start == -1:
            logger.warning("Could not find data assignment in JavaScript file")
            return {}

        json_str = content[json_start:].strip()
        # This regex matches: word: or word :
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', json_str)

        # Remove trailing commas before } or ]
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

        data = json.loads(json_str)
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from JavaScript file: {e}")
        if 'json_str' in locals():
            logger.debug(f"Problematic JSON content (first 500 chars): {json_str[:500]}")
        return {}
    except Exception as e:
        logger.error(f"Failed to fetch nerlist data: {e}")
        return {}


def seed_categories(db: Session) -> None:
    """Insert static categories if they don't exist."""
    for cat_id, cat_name in Category.STATIC_CATEGORIES.items():
        existing = db.query(Category).filter(Category.id == cat_id).first()
        if not existing:
            category = Category(id=cat_id, name=cat_name)
            db.add(category)
            logger.info(f"Added category: {cat_id} - {cat_name}")

    db.commit()


def seed_sources(db: Session, data: dict[str, Any]) -> None:
    """Insert sources and their items from fetched data if they don't exist."""
    if not data:
        logger.warning("No data available to seed sources")
        return

    # Top-level keys are source IDs; each entry has category, title, and items[]
    for key, entry in data.items():
        if not isinstance(entry, dict):
            continue

        source_id = entry.get("id")
        title = entry.get("title")
        category_str = entry.get("category")
        items = entry.get("items", [])

        if not source_id or not title:
            logger.debug(f"Skipping incomplete source entry: {key}")
            continue

        try:
            category_id = int(category_str) if category_str else None
        except (ValueError, TypeError):
            category_id = None

        existing = db.query(Source).filter(Source.title == title).first()
        if not existing:
            source = Source(id=source_id, category_id=category_id, title=title)
            db.add(source)
            logger.info(f"Added source: {source_id} - {title[:50]}")

            for item in items:
                if not isinstance(item, dict):
                    continue
                text = item.get("text")
                url = item.get("url")
                if not text or not url:
                    continue
                db.add(SourceItem(source_id=source_id, text=text, url=url))

    db.commit()


def seed_database(db: Session) -> None:
    """
    Main seeder function: populate categories and sources.
    This is idempotent — existing rows are skipped.
    """
    logger.info("Starting database seeding...")

    # Always seed categories (they're static)
    seed_categories(db)

    # Seed sources from external data
    data = fetch_nerlist_data()
    seed_sources(db, data)

    logger.info("Database seeding completed.")
