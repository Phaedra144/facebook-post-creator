import json
import subprocess
from pathlib import Path

from app.services.image_generator import COVERS_DIR, ImageGenerator

COVER_GEN_DIR = Path(__file__).parent.parent.parent / "cover-gen"


class CoverGenImageGenerator(ImageGenerator):
    def generate(
        self, post_id: int, title: str, subtitle: str = "", fb_post_text: str = ""
    ) -> Path:
        COVERS_DIR.mkdir(exist_ok=True)
        output_file = COVERS_DIR / f"{post_id}.png"

        payload = {
            "title": title,
            "subtitle": subtitle,
            "outputFile": str(output_file),
        }
        result = subprocess.run(
            ["node", "dist/render.js"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=COVER_GEN_DIR,
        )
        if result.returncode != 0:
            raise RuntimeError(f"cover-gen failed: {result.stderr.strip()}")

        return output_file
