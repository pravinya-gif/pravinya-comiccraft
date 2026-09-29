from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from fpdf import FPDF
from PIL import Image
from app.config import BASE_DIR, EXPORTS_DIR

def _plain(text: str) -> str:
    # Core PDF fonts support latin-1 only. Replace unsupported characters safely.
    return str(text or "").encode("latin-1", "replace").decode("latin-1")

def save_pdf(layout: list[dict], title: str = "ComicCraft Comic") -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, _plain(f"Panel {panel.get('panel_number')}: {panel.get('title', '')}"))
        image_url = panel.get("image_path", "")
        if image_url.startswith("/static/"):
            image_path = BASE_DIR / image_url.lstrip("/")
            if image_path.exists():
                try:
                    with Image.open(image_path) as im:
                        iw, ih = im.size
                    max_w, max_h = 175, 105
                    scale = min(max_w / iw, max_h / ih)
                    w, h = iw * scale, ih * scale
                    pdf.image(str(image_path), x=(210-w)/2, w=w, h=h)
                    pdf.ln(5)
                except Exception:
                    pass
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, _plain(panel.get("scene_description", "")))
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 7, _plain(panel.get("caption", "")))
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 7, _plain(panel.get("narration", "")))
        if panel.get("dialogue"):
            pdf.set_font("Helvetica", "I", 12)
            pdf.multi_cell(0, 7, _plain(panel.get("dialogue", "")))
    filename = f"comic-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
    output = EXPORTS_DIR / filename
    pdf.output(str(output))
    return f"/static/exports/{filename}"
