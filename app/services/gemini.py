from pathlib import Path

from google import genai
from google.genai import types

from app.config import settings
from app.services.image_generator import COVERS_DIR, ImageGenerator

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "image_generation.txt"


class GeminiImageGenerator(ImageGenerator):
    def generate(
        self, post_id: int, title: str, subtitle: str = "", fb_post_text: str = ""
    ) -> Path:
        COVERS_DIR.mkdir(exist_ok=True)
        output_file = COVERS_DIR / f"{post_id}.png"

        client = genai.Client(api_key=settings.gemini_api_key)

        prompt_template = PROMPT_FILE.read_text(encoding="utf-8")
        prompt = prompt_template.replace("{FB_POST_TEXT}", fb_post_text)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        # Extract image data from response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                output_file.write_bytes(image_data)
                return output_file

        raise RuntimeError("No image data in Gemini response")
