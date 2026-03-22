import re
from pathlib import Path

from openai import OpenAI

from app.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"

_prompt_template = (Path(__file__).parent.parent / "prompts" / "facebook_post.txt").read_text()

HUNGARIAN_MONTHS = {
    1: "január", 2: "február", 3: "március", 4: "április",
    5: "május", 6: "június", 7: "július", 8: "augusztus",
    9: "szeptember", 10: "október", 11: "november", 12: "december",
}


def extract_dates_from_urls(urls: list[str]) -> list[str]:
    """Extract unique year-month pairs from URLs, returned as Hungarian date strings."""
    seen = set()
    dates = []
    for url in urls:
        match = re.search(r"/(\d{4})[/-](\d{2})[/-]", url)
        if match:
            year, month = int(match.group(1)), int(match.group(2))
            key = (year, month)
            if key not in seen and 1 <= month <= 12:
                seen.add(key)
                dates.append(f"{year} {HUNGARIAN_MONTHS[month]}")
    return dates


def create_facebook_post_text(title: str, summary: str, urls: list[str]) -> str:
    dates = extract_dates_from_urls(urls)
    date_str = ", ".join(dates) if dates else "ismeretlen időpont"
    links_str = "\n".join(urls)

    prompt = (
        _prompt_template
        .replace("{TITLE}", title)
        .replace("{SUMMARY}", summary)
        .replace("{DATE}", date_str)
        .replace("{LINKS}", links_str)
    )

    client = OpenAI(api_key=settings.groq_api_key, base_url=GROQ_BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
