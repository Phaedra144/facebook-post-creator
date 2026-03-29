from datetime import date
from pathlib import Path

from openai import OpenAI

from app.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"

_prompt_template = (Path(__file__).parent.parent / "prompts" / "facebook_post.txt").read_text()

HUNGARIAN_MONTHS = {
    1: "január",
    2: "február",
    3: "március",
    4: "április",
    5: "május",
    6: "június",
    7: "július",
    8: "augusztus",
    9: "szeptember",
    10: "október",
    11: "november",
    12: "december",
}


def create_facebook_post_text(
    title: str, summary: str, category: str, urls: list[str], dates: list[date]
) -> str:
    date_str = (
        ", ".join(f"{d.year} {HUNGARIAN_MONTHS[d.month]}" for d in dates)
        if dates
        else "ismeretlen időpont"
    )
    links_str = "\n".join(urls)

    prompt = (
        _prompt_template.replace("{TITLE}", title)
        .replace("{SUMMARY}", summary)
        .replace("{CATEGORY}", category)
        .replace("{DATES}", date_str)
        .replace("{LINKS}", links_str)
        .replace("{TODAY}", date.today().strftime("%Y. %B %d."))
    )

    client = OpenAI(api_key=settings.groq_api_key, base_url=GROQ_BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
