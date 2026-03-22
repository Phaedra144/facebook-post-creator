from pathlib import Path

from openai import OpenAI

from app.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"

_prompt_template = (Path(__file__).parent.parent / "prompts" / "summarize_source.txt").read_text()


def summarise_articles(article_texts: list[str]) -> str:
    article_list = "; ".join(article_texts)
    prompt = _prompt_template.replace("{ARTICLE_LIST}", article_list)

    client = OpenAI(api_key=settings.groq_api_key, base_url=GROQ_BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
