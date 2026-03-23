from abc import ABC, abstractmethod
from pathlib import Path

COVERS_DIR = Path(__file__).parent.parent.parent / "covers"


class ImageGenerator(ABC):
    @abstractmethod
    def generate(
        self, post_id: int, title: str, subtitle: str = "", fb_post_text: str = ""
    ) -> Path:
        """Generate a cover image for a post. Returns the path to the saved PNG."""
