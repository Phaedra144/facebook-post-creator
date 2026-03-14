# cover-gen

Renders a 1200×630 PNG image from a JSON payload passed via stdin. Built with [Satori](https://github.com/vercel/satori) + [Sharp](https://sharp.pixelplumbing.com/).

## Setup

```bash
npm install
npm run build
```

## JSON schema

All fields are optional and fall back to defaults.

| Field             | Type   | Default                           | Description                       |
| ----------------- | ------ | --------------------------------- | --------------------------------- |
| `title`           | string | `"Hello Satori!"`                 | Large heading text                |
| `subtitle`        | string | `""`                              | Smaller text below the title      |
| `backgroundColor` | string | `"#ffffff"`                       | CSS hex colour for the background |
| `textColor`       | string | `"#000000"`                       | CSS hex colour for the text       |
| `width`           | number | `1200`                            | Output image width in pixels      |
| `height`          | number | `630`                             | Output image height in pixels     |
| `outputFile`      | string | `"output.png"`                    | Path to write the PNG to          |
| `fontFile`        | string | Geist Regular from `node_modules` | Path to a non-variable TTF font   |

## Usage from CLI

Build once, then pipe JSON via stdin:

```bash
# One-shot (build + render)
echo '{"title":"Hello World","subtitle":"My subtitle","backgroundColor":"#1e1e2e","textColor":"#cdd6f4","outputFile":"output.png"}' | npm run render

# After the first build, skip the build step
echo '{"title":"Hello World","outputFile":"output.png"}' | node dist/render.js

# From a JSON file
cat payload.json | node dist/render.js
```

Example `payload.json`:

```json
{
  "title": "My Facebook Post",
  "subtitle": "March 2026",
  "backgroundColor": "#0f172a",
  "textColor": "#f8fafc",
  "outputFile": "cover.png"
}
```

## Usage from Python

```python
import subprocess
import json

def render_cover(payload: dict) -> None:
    """Render a cover image by piping JSON to the Node.js renderer."""
    result = subprocess.run(
        ["node", "dist/render.js"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd="/path/to/cover-gen",  # adjust to your actual path
    )
    if result.returncode != 0:
        raise RuntimeError(f"cover-gen failed: {result.stderr.strip()}")
    print(result.stderr.strip())  # "Image saved to output.png"


render_cover({
    "title": "My Facebook Post",
    "subtitle": "March 2026",
    "backgroundColor": "#0f172a",
    "textColor": "#f8fafc",
    "outputFile": "cover.png",
})
```

If you keep `cover-gen` as a sibling directory, you can resolve the path automatically:

```python
import subprocess
import json
from pathlib import Path

COVER_GEN_DIR = Path(__file__).parent / "cover-gen"

def render_cover(payload: dict, output_file: str = "output.png") -> Path:
    payload = {"outputFile": output_file, **payload}
    result = subprocess.run(
        ["node", "dist/render.js"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=COVER_GEN_DIR,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cover-gen failed: {result.stderr.strip()}")
    return COVER_GEN_DIR / output_file
```

> **Note:** Run `npm run build` inside `cover-gen/` at least once (or after editing `index.jsx`) before calling from Python. The renderer itself (`node dist/render.js`) has no Node.js startup overhead beyond the normal V8 spin-up.

## Rebuilding after edits

```bash
npm run build
```
