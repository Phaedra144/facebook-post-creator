from pathlib import Path

from openai import OpenAI

from app.config import settings

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "openai/gpt-oss-120b"

_prompt_template = (Path(__file__).parent.parent / "prompts" / "summarize_source.txt").read_text()


def summarise_articles(article_texts: list[str]) -> str:
    # Rough heuristic: 1 token ≈ 4 characters. Target ~5500 tokens for articles, leaving
    # ~2500 tokens of headroom for the prompt template and response under the 8000 TPM limit.
    max_total_chars = 22000
    current_chars = 0
    truncated_articles = []

    for text in article_texts:
        if current_chars >= max_total_chars:
            break
        # Truncate individual article if needed
        remaining_budget = max_total_chars - current_chars
        truncated_text = text[:remaining_budget]
        truncated_articles.append(truncated_text)
        current_chars += len(truncated_text) + 2  # +2 for "; "

    article_list = "; ".join(truncated_articles)
    prompt = _prompt_template.replace("{ARTICLE_LIST}", article_list)

    client = OpenAI(api_key=settings.groq_api_key, base_url=GROQ_BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
