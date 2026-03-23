from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    gemini_api_key: str = ""
    fb_page_id: str
    fb_page_access_token: str
    database_url: str = "sqlite:///./facebook-creator.db"

    class Config:
        env_file = ".env"


settings = Settings()
