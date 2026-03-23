from newspaper import Article


def fetch_article(url: str) -> dict:
    article = Article(url)
    article.download()
    article.parse()
    return {"title": article.title, "text": article.text}
