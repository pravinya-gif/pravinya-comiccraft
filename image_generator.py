import re
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.config import PANELS_DIR, HF_API_KEY, HF_IMAGE_MODEL

def _safe_name(prompt: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", prompt.lower()).strip("-")[:36] or "panel"
    return f"{slug}-{uuid.uuid4().hex[:8]}.png"

def _local_fallback(prompt: str, path: Path) -> None:
    """Create a local comic-style card when no image API token is configured."""
    width, height = 1024, 640
    img = Image.new("RGB", (width, height), "#f7e7bd")
    draw = ImageDraw.Draw(img)
    # Halftone-like dots and comic frame
    for y in range(18, height, 28):
        for x in range(18, width, 28):
            draw.ellipse((x, y, x+3, y+3), fill="#e4c98f")
    draw.rounded_rectangle((24, 24, width-24, height-24), radius=22,
                           outline="#25213b", width=12, fill=None)
    draw.polygon([(0, 0), (330, 0), (0, 190)], fill="#f6c445")
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
        small = ImageFont.truetype("DejaVuSans.ttf", 23)
    except OSError:
        font, small = ImageFont.load_default(), ImageFont.load_default()
    draw.text((60, 70), "COMICCRAFT", font=font, fill="#25213b")
    words = prompt[:190]
    lines, line = [], ""
    for word in words.split():
        if len(line + " " + word) > 42:
            lines.append(line); line = word
        else:
            line = (line + " " + word).strip()
    if line: lines.append(line)
    y = 230
    for line in lines[:6]:
        draw.text((65, y), line, font=small, fill="#25213b")
        y += 42
    draw.ellipse((780, 110, 900, 230), fill="#ef6a5b", outline="#25213b", width=8)
    draw.line((810, 170, 870, 170), fill="#25213b", width=8)
    draw.line((840, 140, 840, 200), fill="#25213b", width=8)
    img.save(path)

def generate_image(image_prompt: str, panel_number: int = 1) -> str:
    filename = _safe_name(image_prompt)
    path = PANELS_DIR / filename
    if HF_API_KEY:
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(model=HF_IMAGE_MODEL, token=HF_API_KEY)
            image = client.text_to_image(
                f"comic illustration, {image_prompt}, clear composition, no text, no watermark"
            )
            image.save(path)
        except Exception as exc:
            # Preserve a usable app experience if the hosted model is unavailable.
            _local_fallback(image_prompt, path)
            (PANELS_DIR / f"{path.stem}.txt").write_text(
                f"Image API fallback used: {type(exc).__name__}", encoding="utf-8"
            )
    else:
        _local_fallback(image_prompt, path)
    return f"/static/panels/{filename}"
