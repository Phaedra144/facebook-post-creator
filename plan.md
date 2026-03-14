# Facebook Post Creator — Project Plan

## Overview

An AI content automation pipeline that fetches articles from pre-defined URLs, summarizes them using an LLM, generates images, and posts automatically to a Facebook page.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web framework | FastAPI + Uvicorn |
| Data validation | Pydantic v2 |
| Database | SQLite via SQLAlchemy |
| Article extraction | newspaper3k |
| Summarisation | Groq LLM API |
| Image generation | _(deferred — added by another colleague)_ |
| Social posting | Facebook Pages API (Meta) |

---

## Project Structure

```
facebook-poster/
├── PLAN.md
├── README.md
├── .env                        # secrets (not committed)
├── .env.example
├── requirements.txt
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings via pydantic-settings
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models/
│   │   ├── source.py           # Category + Source ORM models
│   │   └── post.py             # Post (job) ORM model
│   ├── schemas/
│   │   ├── source.py           # Pydantic request/response schemas
│   │   └── post.py
│   ├── routers/
│   │   ├── sources.py          # CRUD endpoints for sources
│   │   └── posts.py            # Trigger / status endpoints
│   ├── services/
│   │   ├── article.py          # newspaper3k extraction
│   │   ├── summariser.py       # Groq API summarisation
│   │   ├── image.py            # Image generation (stub / deferred)
│   │   └── facebook.py         # Facebook Pages API posting
│   └── migrations/
│       └── seed_from_js.py     # One-off: JS htmlData → SQLite
└── tests/
    ├── test_article.py
    ├── test_summariser.py
    └── test_facebook.py
```

---

## Database Schema

### Table: `categories`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | matches original JS key |
| name | TEXT NOT NULL | e.g. "Korrupció" |

### Table: `sources`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | matches original JS id |
| category_id | INTEGER FK → categories.id | |
| text | TEXT NOT NULL | display label |
| url | TEXT NOT NULL UNIQUE | article URL |

### Table: `posts`

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| source_id | INTEGER FK → sources.id | |
| summary | TEXT | generated summary |
| image_url | TEXT | filled by image service |
| fb_post_id | TEXT | returned by Facebook API |
| status | TEXT | `pending` / `summarised` / `image_ready` / `posted` / `error` |
| error_message | TEXT | |
| created_at | DATETIME | |
| posted_at | DATETIME | |

---

## Data Migration (JS → SQLite)

`app/migrations/seed_from_js.py` is a one-off script that:

1. Parses the original `htmlData` JS object (loaded as a Python dict).
2. Inserts each category entry by its id as a `categories` row.
3. Inserts each `items` entry as a `sources` row linked to its category.

Run once before first launch:

```bash
python -m app.migrations.seed_from_js
```

---

## Pipeline Flow

```
POST /posts/run  (or scheduled trigger)
        │
        ▼
1. Pick pending source(s) from DB
        │
        ▼
2. article.py — newspaper3k
   • Download & parse HTML
   • Extract: title, body text, top image hint
        │
        ▼
3. summariser.py — Groq API
   • Prompt: summarise article in 2-3 sentences (Hungarian or EN)
   • Store summary in posts table → status: summarised
        │
        ▼
4. image.py — (DEFERRED)
   • Colleague implements image generation
   • Stores image, updates image_url → status: image_ready
        │
        ▼
5. facebook.py — Meta Pages API
   • POST /me/photos or /me/feed with {url, message}
   • Store fb_post_id → status: posted
```

---

## API Endpoints

### Sources

| Method | Path | Description |
|---|---|---|
| GET | `/sources` | List all sources with category |
| GET | `/sources/{id}` | Get single source |
| POST | `/sources` | Add a new source |
| DELETE | `/sources/{id}` | Remove a source |

### Posts / Pipeline

| Method | Path | Description |
|---|---|---|
| POST | `/posts/run` | Trigger pipeline for one or all pending sources |
| GET | `/posts` | List all posts with status |
| GET | `/posts/{id}` | Get single post detail |
| POST | `/posts/{id}/retry` | Retry a failed post |

---

## Services Detail

### `article.py`

```python
# Uses newspaper3k
from newspaper import Article

def fetch_article(url: str) -> dict:
    article = Article(url)
    article.download()
    article.parse()
    return {"title": article.title, "text": article.text}
```

### `summariser.py`

```python
# Uses Groq SDK
from groq import Groq

def summarise(text: str, title: str) -> str:
    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # or mixtral-8x7b-32768
        messages=[
            {"role": "system", "content": "You are a concise news summariser."},
            {"role": "user", "content": f"Title: {title}\n\n{text}\n\nSummarise in 2-3 sentences."}
        ]
    )
    return response.choices[0].message.content
```

### `facebook.py`

```python
import httpx

GRAPH_URL = "https://graph.facebook.com/v21.0"

def post_to_page(page_id: str, token: str, message: str, image_url: str) -> str:
    resp = httpx.post(
        f"{GRAPH_URL}/{page_id}/feed",
        data={
            "message": message,
            "link": image_url,      # displays as link preview / photo
            "access_token": token,
        }
    )
    resp.raise_for_status()
    return resp.json()["id"]        # Facebook post ID
```

> **Note:** To attach a photo directly (rather than a link preview), use `/page_id/photos` with `url=image_url` and `caption=message`. This endpoint requires the `pages_manage_posts` and `pages_read_engagement` permissions on the Page token.

---

## Environment Variables (`.env`)

```
GROQ_API_KEY=...
FB_PAGE_ID=...
FB_PAGE_ACCESS_TOKEN=...       # long-lived page token
DATABASE_URL=sqlite:///./app.db
```

---

## Required Permissions (Facebook App)

- `pages_manage_posts`
- `pages_read_engagement`
- `pages_show_list`

Generate a long-lived Page Access Token via the [Graph API Explorer](https://developers.facebook.com/tools/explorer/).

---

## Dependencies (`requirements.txt`)

```
fastapi
uvicorn[standard]
pydantic-settings
sqlalchemy
newspaper3k
lxml[html_clean]
groq
httpx
python-dotenv
```

---

## Implementation Order

1. **Project scaffold** — folder structure, `config.py`, `database.py`, `.env.example`
2. **`facebook.py`** — posting service + integration test against FB sandbox
3. **DB models**
4. **Seed script** — migrate JS data to SQLite
5. **`article.py`** — newspaper3k extraction + unit test
6. **`summariser.py`** — Groq integration + unit test
7. **Posts pipeline API** — `/posts/run` wiring up steps 4→5
8. **`image.py` stub** — placeholder so pipeline does not break before colleague delivers
9. **End-to-end test** — full run from DB source → Facebook post
