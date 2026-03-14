import httpx

from app.config import settings

GRAPH_URL = "https://graph.facebook.com/v25.0"


async def post_to_page(message: str, image_url: str | None = None) -> str:
    page_id = settings.fb_page_id
    page_access_token = settings.fb_page_access_token

    data: dict = {"message": message}
    if image_url:
        data["link"] = image_url

    params = {"access_token": page_access_token}

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{GRAPH_URL}/{page_id}/feed", data=data, params=params)
        if resp.status_code != 200:
            error_detail = resp.json() if resp.headers.get('content-type') == 'application/json' else resp.text
            raise Exception(f"Facebook API error ({resp.status_code}): {error_detail}")
        return resp.json()["id"]


async def post_to_page_with_photo(message: str, image_url: str) -> str:
    page_id = settings.fb_page_id
    page_access_token = settings.fb_page_access_token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/{page_id}/photos",
            data={
                "url": image_url,
                "caption": message,
                "access_token": page_access_token,
            },
        )
        resp.raise_for_status()
        return resp.json()["id"]
