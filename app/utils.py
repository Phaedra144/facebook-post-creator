import re
from datetime import date


def extract_dates_from_urls(urls: list[str]) -> list[date | None]:
    """Extract a year-month date from each URL.

    Returns a list of datetime.date(year, month, 1) values, one per input URL.
    Returns None for URLs where no date pattern is found.
    """
    results = []
    for url in urls:
        match = re.search(r"/(\d{4})[/-](\d{2})[/-]", url)
        if not match:
            match = re.search(r"/(\d{4})(\d{2})\d{2}[_/]", url)
        if match:
            year, month = int(match.group(1)), int(match.group(2))
            results.append(date(year, month, 1) if 1 <= month <= 12 else None)
        else:
            results.append(None)
    return results
